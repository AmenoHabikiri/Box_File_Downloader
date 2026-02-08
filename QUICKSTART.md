# Quick Start Guide

Get started with Box Folder Downloader in 3 steps.

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `selenium` - Browser automation
- `requests` - HTTP client
- `tqdm` - Progress bars

## 2. Download Files

### Using Selenium (Recommended)

```bash
# Interactive mode - watch the browser work
python box_selenium_downloader.py "https://rak.app.box.com/s/YOUR_SHARED_LINK"

# Headless mode - runs in background
python box_selenium_downloader.py "https://rak.app.box.com/s/YOUR_SHARED_LINK" --headless
```

### Example with your RAK Box link:

```bash
python box_selenium_downloader.py "https://rak.app.box.com/s/28k3u2r6xglkx4qh38driemzn3mcj3kq" --headless
```

## 3. Extract Downloaded Files

```bash
./extract_and_organize.sh
```

Files will be extracted to `extracted_files/` directory.

## Complete Workflow

```bash
# 1. Download from Box
python box_selenium_downloader.py "YOUR_BOX_LINK" --headless -v

# 2. Extract files
./extract_and_organize.sh

# 3. Use the files
ls extracted_files/
```

## Troubleshooting

### Chrome driver not found
```bash
# macOS
brew install chromedriver

# The error usually auto-resolves with selenium 4.x
```

### No files downloaded
- Check if the Box link is publicly accessible
- Try without `--headless` to see what happens
- Use `-v` flag for verbose output

### Permission denied
```bash
chmod +x box_selenium_downloader.py extract_and_organize.sh
```

## Advanced Usage

### Custom output directory
```bash
python box_selenium_downloader.py "BOX_LINK" --output ~/Desktop/box_files
```

### Verbose mode
```bash
python box_selenium_downloader.py "BOX_LINK" --headless -v
```

### Using config file (API method)
```bash
cp config.example.json config.json
# Edit config.json with your links
python box_downloader.py --config config.json
```

## What Gets Downloaded?

Box downloads entire folders as ZIP files containing:
- Excel files (.xlsx)
- CSV files (.csv)
- PDFs (.pdf)
- Images (.png, .jpg)
- Any other files in the shared folder

## Integration Example

Use in a shell script:

```bash
#!/bin/bash
BOX_LINK="https://rak.app.box.com/s/28k3u2r6xglkx4qh38driemzn3mcj3kq"

# Download
python box_selenium_downloader.py "$BOX_LINK" --headless

# Extract
./extract_and_organize.sh

# Process files
python process_reports.py extracted_files/*.xlsx
```

## Automation with Cron

```bash
# Download Box files daily at 9 AM
0 9 * * * cd /path/to/box-folder-downloader && python box_selenium_downloader.py "BOX_LINK" --headless
```

## Next Steps

1. Star the repo if you find it useful
2. Report issues on GitHub
3. Contribute improvements
