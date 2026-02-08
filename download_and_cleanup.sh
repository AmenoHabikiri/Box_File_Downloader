#!/bin/bash

# Integrated workflow: Download from Box and keep only latest report

set -e  # Exit on error

BOX_LINK="${1:-https://rak.app.box.com/s/28k3u2r6xglkx4qh38driemzn3mcj3kq}"
DOWNLOAD_DIR="downloads"
EXTRACT_DIR="extracted_files"

echo "================================================================"
echo "Box Download & Cleanup Workflow"
echo "================================================================"
echo ""
echo "Box Link: $BOX_LINK"
echo ""

# Step 1: Download from Box
echo "Step 1: Downloading from Box..."
python3 box_selenium_downloader.py "$BOX_LINK" --headless

if [ $? -ne 0 ]; then
    echo "✗ Download failed"
    exit 1
fi

echo ""

# Step 2: Extract files
echo "Step 2: Extracting files..."
mkdir -p "$EXTRACT_DIR"

if ls "$DOWNLOAD_DIR"/*.zip 1> /dev/null 2>&1; then
    for zip_file in "$DOWNLOAD_DIR"/*.zip; do
        echo "  Extracting: $(basename "$zip_file")"
        unzip -q -o "$zip_file" -d "$EXTRACT_DIR"
    done
    echo "✓ Extraction complete"
else
    echo "✗ No zip files found"
    exit 1
fi

echo ""

# Step 3: Cleanup - keep only latest report
echo "Step 3: Cleaning up (keeping only latest report)..."
python3 cleanup_reports.py "$EXTRACT_DIR" -v

echo ""
echo "================================================================"
echo "✓ Workflow Complete!"
echo "================================================================"
echo ""
echo "Latest report available in:"
find "$EXTRACT_DIR" -name "Data_Volume_Report_*.xlsx" -type f
echo ""
