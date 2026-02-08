#!/bin/bash

# Manual Box Download Helper
# Opens Box shared link in browser for manual download

SHARED_LINK="${1:-https://rak.app.box.com/s/28k3u2r6xglkx4qh38driemzn3mcj3kq}"
DOWNLOAD_DIR="downloads"

echo "================================================================"
echo "Box Manual Download Helper"
echo "================================================================"
echo ""
echo "Box shared folders require browser authentication for downloads."
echo "This script will open the folder in your browser."
echo ""
echo "Shared Link: $SHARED_LINK"
echo ""
echo "Manual Download Steps:"
echo "1. Browser will open with the shared folder"
echo "2. Click the 'Download' button for each file"
echo "3. Or use 'Download Folder' to get all files as a zip"
echo "4. Files will be saved to your Downloads folder"
echo ""
echo "Then move files to: $(pwd)/$DOWNLOAD_DIR/"
echo ""
read -p "Press Enter to open in browser..."

# Create downloads directory
mkdir -p "$DOWNLOAD_DIR"

# Open in browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$SHARED_LINK"
# Linux
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$SHARED_LINK" 2>/dev/null || echo "Please open: $SHARED_LINK"
# Windows/Git Bash
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    start "$SHARED_LINK"
else
    echo "Please manually open: $SHARED_LINK"
fi

echo ""
echo "After downloading, run:"
echo "  mv ~/Downloads/*.xlsx ./$DOWNLOAD_DIR/"
echo ""
