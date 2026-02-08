#!/bin/bash

# Extract and organize downloaded Box files

DOWNLOAD_DIR="downloads"
OUTPUT_DIR="extracted_files"

echo "================================================================"
echo "Box Download Extractor"
echo "================================================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Find and extract all zip files
if ls "$DOWNLOAD_DIR"/*.zip 1> /dev/null 2>&1; then
    echo "Found zip files. Extracting..."
    for zip_file in "$DOWNLOAD_DIR"/*.zip; do
        echo "  Extracting: $(basename "$zip_file")"
        unzip -q -o "$zip_file" -d "$OUTPUT_DIR"
    done
    echo ""
    echo "✓ Extraction complete"
else
    echo "No zip files found in $DOWNLOAD_DIR"
fi

# List extracted files
echo ""
echo "Extracted files:"
find "$OUTPUT_DIR" -type f -exec ls -lh {} \; | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "Files available in: $(pwd)/$OUTPUT_DIR/"
echo ""
