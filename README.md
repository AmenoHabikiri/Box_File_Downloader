# Box Folder Downloader

> **Automated tool to download Box shared folders and keep only the latest files**

A command-line tool that downloads files from Box shared folders without API credentials, automatically parses dates from filenames, and keeps only the most recent reports while cleaning up old files and images.

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.7+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [One-Command Workflow](#one-command-workflow-recommended)
  - [Selenium Browser Automation](#selenium-browser-automation)
  - [Cleanup Only](#cleanup-only)
  - [Direct API Method](#direct-api-method-fallback)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Automation](#automation)
- [Examples](#examples)
- [Test Results](#test-results)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

✅ **Automated Download**
- Download entire Box shared folders from terminal
- Selenium browser automation (works with most Box links)
- No Box Developer API credentials required
- Headless mode for background operation

✅ **Intelligent Cleanup**
- Parses dates from `Data_Volume_Report_DDMMYYYY.xlsx` filenames
- Automatically keeps **only** the most recent report
- Deletes **all** older report files
- Deletes **all** image files (.png, .jpg, .jpeg, .gif, .bmp)

✅ **Easy to Use**
- One-command workflow script
- Safe dry-run mode for previewing changes
- Verbose logging for transparency
- Progress tracking with visual indicators

✅ **Production Ready**
- Comprehensive error handling
- Well-documented with examples
- Tested and verified
- Ready for daily automation

## Quick Start

```bash
# 1. Navigate to repository
cd /path/to/box-folder-downloader

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run with one command
./download_and_cleanup.sh "https://your-box-link.com/s/xxxxx"

# 4. Access the latest report
ls extracted_files/*/Data_Volume_Report_*.xlsx
```

That's it! The script downloads, extracts, and keeps only the latest report automatically.

## Installation

### Prerequisites

- Python 3.7 or higher
- Chrome browser (for Selenium automation)
- pip (Python package manager)

### Install Steps

```bash
# Clone or download the repository
git clone <repository-url>
cd box-folder-downloader

# Install Python dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x *.sh *.py

# Verify installation
python box_selenium_downloader.py --help
```

### Dependencies

- `selenium>=4.15.0` - Browser automation
- `requests>=2.31.0` - HTTP client
- `tqdm>=4.66.0` - Progress bars

## Usage

### One-Command Workflow (Recommended)

The simplest way to download and cleanup:

```bash
# Download, extract, and keep only latest report
./download_and_cleanup.sh "https://rak.app.box.com/s/YOUR_LINK"

# Or use the default configured link
./download_and_cleanup.sh
```

**What it does:**
1. ✅ Downloads files from Box using Selenium (headless Chrome)
2. ✅ Extracts the zip archive
3. ✅ Parses dates from Excel filenames
4. ✅ Keeps only the most recent `Data_Volume_Report_*.xlsx` file
5. ✅ Deletes all older reports
6. ✅ Deletes all image files

**Result:** Only the latest report remains in `extracted_files/`

### Selenium Browser Automation

Manual control over the download process:

```bash
# Interactive mode (see browser window)
python box_selenium_downloader.py "BOX_LINK"

# Headless mode (runs in background)
python box_selenium_downloader.py "BOX_LINK" --headless

# Verbose output for debugging
python box_selenium_downloader.py "BOX_LINK" --headless -v

# Custom output directory
python box_selenium_downloader.py "BOX_LINK" --output ./my_downloads
```

After downloading, run cleanup separately:

```bash
# Extract downloaded files
unzip -o downloads/*.zip -d extracted_files/

# Preview cleanup (safe dry-run)
python cleanup_reports.py extracted_files --dry-run

# Actually cleanup
python cleanup_reports.py extracted_files -v
```

### Cleanup Only

If you already have files downloaded and just need cleanup:

```bash
# Preview what will be deleted (dry-run)
python cleanup_reports.py extracted_files --dry-run -v

# Actually delete old files and images
python cleanup_reports.py extracted_files -v

# Clean a specific directory
python cleanup_reports.py "path/to/folder" -v
```

**Cleanup Logic:**
- Finds all files matching `Data_Volume_Report_DDMMYYYY.xlsx`
- Parses dates: DD=day, MM=month, YYYY=year
- Keeps the file with the most recent date
- Deletes all other report files
- Deletes all image files (any extension)

### Direct API Method (Fallback)

Direct API calls without browser (limited support):

```bash
# Basic download
python box_downloader.py "BOX_LINK"

# With custom output
python box_downloader.py "BOX_LINK" --output ./downloads

# Verbose mode
python box_downloader.py "BOX_LINK" -v
```

**Note:** This method may not work with all Box shared links. Use Selenium method for reliability.

## How It Works

### Download Process (Selenium)

1. **Browser Launch**: Starts Chrome in headless mode
2. **Navigate**: Opens the Box shared link
3. **Download**: Clicks "Download Folder" button
4. **Wait**: Monitors for download completion
5. **Result**: Entire folder downloaded as zip file

### Cleanup Process

1. **Scan**: Walks directory tree to find Excel files
2. **Parse**: Extracts date from filename pattern `Data_Volume_Report_DDMMYYYY.xlsx`
3. **Compare**: Identifies the most recent file by date
4. **Clean**: Deletes older reports and all images
5. **Verify**: Reports results with statistics

### Example Workflow

**Input Files:**
```
Radcom Daily HealthCheck Report/
  ├── Data_Volume_Report_07022026.xlsx  (Date: 2026-02-07)
  ├── Data_Volume_Report_04022026.xlsx  (Date: 2026-02-04)
  └── image001.png
```

**After Cleanup:**
```
Radcom Daily HealthCheck Report/
  └── Data_Volume_Report_07022026.xlsx  ✅ Latest only
```

Deleted:
- ❌ `Data_Volume_Report_04022026.xlsx` (older)
- ❌ `image001.png` (image)

## Configuration

### Using Configuration File

Create `config.json`:

```json
{
  "shared_links": [
    "https://rak.app.box.com/s/your-link-1",
    "https://rak.app.box.com/s/your-link-2"
  ],
  "output_dir": "downloads",
  "file_types": [".xlsx", ".csv", ".pdf"]
}
```

Run with config:

```bash
python box_downloader.py --config config.json
```

### Environment Variables

Edit `download_and_cleanup.sh` to set default Box link:

```bash
BOX_LINK="${1:-https://rak.app.box.com/s/YOUR_DEFAULT_LINK}"
```

## Automation

### Daily Cron Job

Run automatically every day at 9:00 AM:

```bash
# Edit crontab
crontab -e

# Add this line
0 9 * * * cd /path/to/box-folder-downloader && ./download_and_cleanup.sh >> logs/download.log 2>&1
```

### With Logging

Create logs directory and run with output:

```bash
mkdir -p logs
./download_and_cleanup.sh 2>&1 | tee logs/download_$(date +%Y%m%d_%H%M%S).log
```

### Integration with Scripts

```bash
#!/bin/bash
# your_workflow.sh

# Step 1: Download latest report
cd /path/to/box-folder-downloader
./download_and_cleanup.sh

# Step 2: Get the latest report path
LATEST_REPORT=$(find extracted_files -name "Data_Volume_Report_*.xlsx" -type f)

# Step 3: Process with your script
python your_analysis.py "$LATEST_REPORT"
```

### Python Integration

```python
import subprocess
import glob
import pandas as pd

# Download and cleanup
result = subprocess.run(
    ['bash', '-c', 'cd ~/box-folder-downloader && ./download_and_cleanup.sh'],
    capture_output=True, text=True
)

if result.returncode == 0:
    # Find the latest report
    reports = glob.glob('~/box-folder-downloader/extracted_files/**/Data_Volume_Report_*.xlsx', recursive=True)
    if reports:
        latest_report = reports[0]

        # Process the Excel file
        df = pd.read_excel(latest_report)
        print(f"Loaded: {latest_report}")
        print(f"Rows: {len(df)}")
```

## Examples

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for:
- Daily report download workflows
- Scheduled automation examples
- Integration patterns
- Error handling
- Multiple folder downloads
- Docker container usage
- Archive and backup strategies

## Test Results

### Verified Test Case

**Box Folder:** RAK Radcom Daily HealthCheck Report

**Input:**
- `Data_Volume_Report_07022026.xlsx` (Feb 7, 2026) - 341 KB
- `Data_Volume_Report_04022026.xlsx` (Feb 4, 2026) - 340 KB
- `image001.png` - 83 KB

**Command:**
```bash
./download_and_cleanup.sh "https://rak.app.box.com/s/28k3u2r6xglkx4qh38driemzn3mcj3kq"
```

**Result:**
```
✓ Downloaded: 1 file (766 KB zip)
✓ Extracted: 3 files
✓ Kept: Data_Volume_Report_07022026.xlsx (Feb 7, 2026)
✓ Deleted: Data_Volume_Report_04022026.xlsx (Feb 4, 2026)
✓ Deleted: image001.png
```

**Final State:**
- ✅ Only `Data_Volume_Report_07022026.xlsx` remains
- ✅ File verified as valid Microsoft Excel 2007+ format
- ✅ Workflow completed in ~30 seconds

**Status:** ✅ **PASSED**

## Troubleshooting

### Chrome Driver Issues

**Problem:** Selenium can't find Chrome driver

**Solution:**
```bash
# macOS
brew install chromedriver

# Or let Selenium auto-download (should work by default)
```

### Download Fails

**Problem:** "Could not fetch folder items" or download fails

**Solutions:**
1. Verify Box link is publicly accessible
2. Check if download permissions are enabled
3. Try without `--headless` to see what happens
4. Use `-v` flag for verbose output

### No Files Cleaned Up

**Problem:** Cleanup reports "No files found"

**Solution:**
```bash
# Check if extraction worked
ls -R extracted_files/

# Make sure you're pointing to the right directory
python cleanup_reports.py "extracted_files/Radcom Daily HealthCheck Report" -v
```

### Date Parsing Fails

**Problem:** Cleanup can't parse dates from filenames

**Requirements:**
- Filename must match pattern: `Data_Volume_Report_DDMMYYYY.xlsx`
- Example: `Data_Volume_Report_07022026.xlsx` = Feb 7, 2026
- Format: DD=day (01-31), MM=month (01-12), YYYY=year (e.g., 2026)

### Permission Denied

**Problem:** `Permission denied` when running scripts

**Solution:**
```bash
chmod +x *.sh *.py
```

### Box Requires Login

**Problem:** Box asks for login even with shared link

**Solution:**
- Use `box_cleanup_selenium.py` with credentials for direct Box cleanup
- Or download manually and use local cleanup: `cleanup_reports.py`

## Project Structure

```
box-folder-downloader/
├── download_and_cleanup.sh         # ⭐ Main workflow script
├── box_selenium_downloader.py      # Selenium download automation
├── cleanup_reports.py              # Date-based cleanup utility
├── box_cleanup_selenium.py         # Direct Box cleanup (needs login)
├── box_downloader.py               # API-based downloader (fallback)
├── extract_and_organize.sh         # Extraction helper script
├── README.md                       # This file
├── QUICKSTART.md                   # Quick setup guide
├── USAGE_EXAMPLES.md               # Real-world examples
├── IMPLEMENTATION_SUMMARY.md       # Technical documentation
├── LICENSE                         # MIT License
├── requirements.txt                # Python dependencies
├── config.example.json             # Configuration template
├── .gitignore                      # Git ignore rules
├── downloads/                      # Downloaded zip files (gitignored)
└── extracted_files/                # Extracted & cleaned files (gitignored)
```

## Contributing

Contributions are welcome! Areas for improvement:
- Support for additional date formats
- Email/Slack notifications
- Web UI for configuration
- Docker container
- Additional file type patterns
- Archive functionality

Please submit Pull Requests or open Issues on GitHub.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:
- [Selenium](https://www.selenium.dev/) - Browser automation
- [Requests](https://requests.readthedocs.io/) - HTTP library
- [tqdm](https://tqdm.github.io/) - Progress bars

## Support

- 📖 Documentation: See [QUICKSTART.md](QUICKSTART.md) and [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- 🐛 Issues: Report bugs via GitHub Issues
- 💡 Questions: Open a discussion or issue

---

**Status:** ✅ Production Ready | **Version:** 1.0.0 | **Last Updated:** February 2026
