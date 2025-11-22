#!/usr/bin/env python3
"""
YouTube to MP3 Converter
A GTK4 application for downloading YouTube videos and converting them to MP3
"""

import gi
import os
import sys
import threading
import subprocess
import tempfile
import shutil
import re
from pathlib import Path

gi.require_version('Gtk', '4.0')

# Try to import Adw (libadwaita), but make it optional
try:
    gi.require_version('Adw', '1')
    from gi.repository import Adw
    HAS_ADW = True
except ValueError:
    HAS_ADW = False
    Adw = None

from gi.repository import Gtk, GLib, Gio

# Use Adw.ApplicationWindow if available, otherwise use Gtk.ApplicationWindow
if HAS_ADW:
    BaseWindow = Adw.ApplicationWindow
    BaseApp = Adw.Application
else:
    BaseWindow = Gtk.ApplicationWindow
    BaseApp = Gtk.Application


class YouTube2MP3Window(BaseWindow):
    def __init__(self, app):
        super().__init__(application=app, title="YouTube to MP3 Converter")
        self.set_default_size(600, 400)
        
        # Initialize variables
        self.temp_dir = None
        self.download_thread = None
        self.is_downloading = False
        
        # Create main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        
        # Use set_content for Adw, set_child for Gtk
        if HAS_ADW:
            self.set_content(main_box)
        else:
            self.set_child(main_box)
        
        # Header (use Gtk.HeaderBar if Adw is not available)
        # For Adw, we can add header to content; for Gtk, we set it as titlebar
        if HAS_ADW:
            header = Adw.HeaderBar()
            main_box.append(header)
        else:
            header = Gtk.HeaderBar()
            self.set_titlebar(header)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='xx-large' weight='bold'>YouTube to MP3</span>")
        title_label.set_halign(Gtk.Align.START)
        main_box.append(title_label)
        
        # YouTube URL entry
        url_frame = Gtk.Frame()
        url_frame.set_label("YouTube URL")
        url_frame.set_label_widget(Gtk.Label(label="YouTube URL"))
        url_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        url_frame.set_child(url_box)
        
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("https://www.youtube.com/watch?v=...")
        self.url_entry.set_hexpand(True)
        url_box.append(self.url_entry)
        main_box.append(url_frame)
        
        # Folder selection
        folder_frame = Gtk.Frame()
        folder_frame.set_label("Save Folder")
        folder_frame.set_label_widget(Gtk.Label(label="Save Folder"))
        folder_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        folder_frame.set_child(folder_box)
        
        # Get default Downloads folder
        default_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(default_folder):
            default_folder = os.path.expanduser("~")
        
        self.folder_entry = Gtk.Entry()
        self.folder_entry.set_text(default_folder)
        self.folder_entry.set_placeholder_text("Select folder to save MP3 file...")
        self.folder_entry.set_hexpand(True)
        folder_box.append(self.folder_entry)
        
        self.folder_button = Gtk.Button(label="Browse")
        self.folder_button.connect("clicked", self.on_browse_folder_clicked)
        folder_box.append(self.folder_button)
        main_box.append(folder_frame)
        
        # Filename entry
        filename_frame = Gtk.Frame()
        filename_frame.set_label("File Name")
        filename_frame.set_label_widget(Gtk.Label(label="File Name"))
        filename_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        filename_frame.set_child(filename_box)
        
        self.filename_entry = Gtk.Entry()
        self.filename_entry.set_placeholder_text("Enter filename (without .mp3 extension)")
        self.filename_entry.set_hexpand(True)
        filename_box.append(self.filename_entry)
        main_box.append(filename_frame)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Ready")
        self.progress_bar.set_fraction(0.0)
        main_box.append(self.progress_bar)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_wrap(True)
        main_box.append(self.status_label)
        
        # Download button
        self.download_button = Gtk.Button(label="Download & Convert")
        self.download_button.add_css_class("suggested-action")
        self.download_button.connect("clicked", self.on_download_clicked)
        main_box.append(self.download_button)
        
        # Spacer
        main_box.append(Gtk.Label())  # Spacer
        
    def on_browse_folder_clicked(self, button):
        """Open folder selection dialog"""
        dialog = Gtk.FileDialog(title="Select Folder", modal=True)
        dialog.set_accept_label("Select")
        
        # Set initial folder if one is already selected
        current_folder = self.folder_entry.get_text().strip()
        if current_folder and os.path.exists(current_folder):
            try:
                initial_file = Gio.File.new_for_path(current_folder)
                dialog.set_initial_folder(initial_file)
            except:
                pass
        
        dialog.select_folder(self, None, self.on_folder_dialog_response)
    
    def on_folder_dialog_response(self, dialog, result):
        """Handle folder dialog response"""
        try:
            file = dialog.select_folder_finish(result)
            if file:
                folder_path = file.get_path()
                self.folder_entry.set_text(folder_path)
        except Exception as e:
            print(f"Error selecting folder: {e}")
    
    def on_download_clicked(self, button):
        """Start download and conversion process"""
        url = self.url_entry.get_text().strip()
        folder_path = self.folder_entry.get_text().strip()
        filename = self.filename_entry.get_text().strip()
        
        # Validate inputs
        if not url:
            self.show_error("Please enter a YouTube URL")
            return
        
        if not folder_path:
            self.show_error("Please select a save folder")
            return
        
        if not os.path.exists(folder_path):
            self.show_error("Selected folder does not exist")
            return
        
        if not filename:
            self.show_error("Please enter a filename")
            return
        
        # Build full file path
        if not filename.endswith('.mp3'):
            filename += '.mp3'
        file_path = os.path.join(folder_path, filename)
        
        if self.is_downloading:
            self.show_error("Download already in progress")
            return
        
        # Disable button and start process
        self.download_button.set_sensitive(False)
        self.is_downloading = True
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_text("Starting...")
        self.status_label.set_text("")
        
        # Start download in separate thread
        self.download_thread = threading.Thread(
            target=self.download_and_convert,
            args=(url, file_path),
            daemon=True
        )
        self.download_thread.start()
    
    def download_and_convert(self, url, output_path):
        """Download video and convert to MP3 (runs in separate thread)"""
        try:
            # Create temp directory
            self.temp_dir = tempfile.mkdtemp()
            temp_video = os.path.join(self.temp_dir, "video.%(ext)s")
            
            # Check for yt-dlp
            ytdlp_cmd = shutil.which("yt-dlp")
            if not ytdlp_cmd:
                GLib.idle_add(self.show_error, "yt-dlp not found. Please install it: pacman -S yt-dlp")
                GLib.idle_add(self.reset_ui)
                return
            
            # Check for ffmpeg
            ffmpeg_cmd = shutil.which("ffmpeg")
            if not ffmpeg_cmd:
                GLib.idle_add(self.show_error, "ffmpeg not found. Please install it: pacman -S ffmpeg")
                GLib.idle_add(self.reset_ui)
                return
            
            # Update status
            GLib.idle_add(self.update_status, "Downloading video...")
            GLib.idle_add(self.update_progress, 0.1, "Downloading...")
            
            # Download video
            download_cmd = [
                ytdlp_cmd,
                url,
                "-o", temp_video,
                "--no-playlist",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "--embed-thumbnail",
                "-f", "bestaudio/best"
            ]
            
            process = subprocess.Popen(
                download_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # yt-dlp outputs progress to stderr, merge with stdout
                universal_newlines=True,
                cwd=self.temp_dir,
                bufsize=1
            )
            
            # Monitor download progress
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                output_lines.append(line)
                # Try to extract progress from yt-dlp output
                if "%" in line or "Downloading" in line or "ETA" in line:
                    try:
                        # Update progress (yt-dlp outputs to stderr which we merged)
                        if "Downloading" in line:
                            # Try to extract percentage
                            match = re.search(r'(\d+(?:\.\d+)?)%', line)
                            if match:
                                percent = float(match.group(1)) / 100.0
                                GLib.idle_add(self.update_progress, 0.1 + percent * 0.6, f"Downloading... {match.group(1)}%")
                            else:
                                GLib.idle_add(self.update_progress, 0.3, "Downloading...")
                    except:
                        pass
            
            process.wait()
            
            if process.returncode != 0:
                error_msg = '\n'.join(output_lines[-5:]) if output_lines else "Download failed"
                GLib.idle_add(self.show_error, f"Download failed: {error_msg}")
                GLib.idle_add(self.reset_ui)
                return
            
            # Find downloaded file
            downloaded_files = list(Path(self.temp_dir).glob("*"))
            video_file = None
            for f in downloaded_files:
                if f.is_file() and f.suffix in ['.mp3', '.m4a', '.webm', '.opus']:
                    video_file = str(f)
                    break
            
            if not video_file:
                GLib.idle_add(self.show_error, "Downloaded file not found")
                GLib.idle_add(self.reset_ui)
                return
            
            # If already MP3, just move it
            if video_file.endswith('.mp3'):
                GLib.idle_add(self.update_status, "Moving file...")
                GLib.idle_add(self.update_progress, 0.9, "Finalizing...")
                shutil.move(video_file, output_path)
            else:
                # Convert to MP3
                GLib.idle_add(self.update_status, "Converting to MP3...")
                GLib.idle_add(self.update_progress, 0.7, "Converting...")
                
                convert_cmd = [
                    ffmpeg_cmd,
                    "-i", video_file,
                    "-codec:a", "libmp3lame",
                    "-q:a", "0",
                    "-y",  # Overwrite output file
                    output_path
                ]
                
                convert_process = subprocess.run(
                    convert_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if convert_process.returncode != 0:
                    GLib.idle_add(self.show_error, f"Conversion failed: {convert_process.stderr}")
                    GLib.idle_add(self.reset_ui)
                    return
            
            # Success!
            GLib.idle_add(self.update_progress, 1.0, "Complete!")
            GLib.idle_add(self.update_status, f"✓ Successfully converted! Saved to: {output_path}")
            GLib.idle_add(self.reset_ui)
            
        except Exception as e:
            GLib.idle_add(self.show_error, f"Error: {str(e)}")
            GLib.idle_add(self.reset_ui)
        finally:
            # Cleanup temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                except:
                    pass
    
    def update_progress(self, fraction, text):
        """Update progress bar (called from thread via GLib.idle_add)"""
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(text)
    
    def update_status(self, message):
        """Update status label (called from thread via GLib.idle_add)"""
        self.status_label.set_text(message)
    
    def show_error(self, message):
        """Show error message"""
        self.status_label.set_text(f"✗ {message}")
        self.status_label.add_css_class("error")
    
    def reset_ui(self):
        """Reset UI after download completes"""
        self.is_downloading = False
        self.download_button.set_sensitive(True)
        self.status_label.remove_css_class("error")


class YouTube2MP3App(BaseApp):
    def __init__(self):
        super().__init__(application_id="com.youtube2mp3.app")
        self.connect("activate", self.on_activate)
        
        # Set application icon if available
        icon_paths = [
            "youtube2mp3.png",
            "youtube2mp3.svg",
            "youtube2mp3.ico",
            os.path.join(os.path.dirname(__file__), "youtube2mp3.png"),
            os.path.join(os.path.dirname(__file__), "youtube2mp3.svg"),
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    icon = Gio.File.new_for_path(icon_path)
                    self.set_default_icon_file(icon.get_path())
                    break
                except:
                    pass
    
    def on_activate(self, app):
        self.win = YouTube2MP3Window(self)
        self.win.present()


def main():
    app = YouTube2MP3App()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()

