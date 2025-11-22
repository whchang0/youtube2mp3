# YouTube to MP3 Converter

A GTK4 application for downloading YouTube videos and converting them to MP3 format.

## Features

- Download YouTube videos
- Convert to MP3 format
- Beautiful GTK4 interface
- Progress tracking
- File save dialog

## Requirements

### MSYS2 UCRT64 Environment

1. **Python packages (required):**
   ```bash
   pacman -S mingw-w64-ucrt-x86_64-python-pygobject
   pacman -S mingw-w64-ucrt-x86_64-python-gobject
   ```
   
   **Optional (for modern UI):**
   ```bash
   pacman -S mingw-w64-ucrt-x86_64-libadwaita
   ```
   Note: The application will work without libadwaita, but with a slightly different appearance.

2. **Dependencies:**
   ```bash
   pacman -S mingw-w64-ucrt-x86_64-yt-dlp
   pacman -S mingw-w64-ucrt-x86_64-ffmpeg
   ```

## Installation

1. Make sure you're in MSYS2 UCRT64 terminal
2. Install dependencies (see Requirements above)
3. Run the application:
   ```bash
   python youtube2mp3.py
   ```

## Usage

1. Enter a YouTube URL in the URL field
2. Click "Browse" to select where to save the MP3 file
3. Click "Download & Convert" to start the process
4. Wait for the progress bar to complete
5. Your MP3 file will be saved at the specified location

## Icon

The application includes an SVG icon (`youtube2mp3.svg`). To generate PNG and ICO formats:

1. Install Pillow (if not already installed):
   ```bash
   pacman -S mingw-w64-ucrt-x86_64-python-pillow
   ```

2. Run the icon generator:
   ```bash
   python create_icon.py
   ```

This will create `youtube2mp3.png` and `youtube2mp3.ico` files.

## License

This project is provided as-is for educational purposes.

