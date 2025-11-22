#!/bin/bash
# Simple launcher script for YouTube to MP3 Converter

# Check if we're in MSYS2
if [ -z "$MSYSTEM" ]; then
    echo "Warning: This script is designed for MSYS2 UCRT64 environment"
    echo "Please run from MSYS2 UCRT64 terminal"
fi

# Run the application
python youtube2mp3.py "$@"

