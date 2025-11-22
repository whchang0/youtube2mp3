#!/bin/bash
# Setup script for YouTube to MP3 Converter in MSYS2 UCRT64

echo "Setting up YouTube to MP3 Converter in MSYS2 UCRT64..."
echo ""

# Update package database
echo "Updating package database..."
pacman -Sy

# Install Python and PyGObject
echo "Installing Python and PyGObject..."
pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-python \
    mingw-w64-ucrt-x86_64-python-pip \
    mingw-w64-ucrt-x86_64-python-pygobject \
    mingw-w64-ucrt-x86_64-gobject-introspection

# Install libadwaita (optional, for modern UI)
echo "Installing libadwaita (optional)..."
pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-libadwaita || echo "libadwaita installation failed, but app will work without it"

# Install yt-dlp
echo "Installing yt-dlp..."
pacman -S --needed --noconfirm yt-dlp

# Install ffmpeg
echo "Installing ffmpeg..."
pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-ffmpeg

# Install Pillow for icon generation (optional)
echo "Installing Pillow for icon generation..."
pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-python-pillow

echo ""
echo "Setup complete!"
echo ""
echo "To generate the icon, run:"
echo "  python create_icon.py"
echo ""
echo "To run the application, use:"
echo "  python youtube2mp3.py"
echo ""

