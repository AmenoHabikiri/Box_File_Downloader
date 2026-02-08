# Box Folder Downloader

A command-line tool to download files from Box shared folders without requiring Box Developer API credentials.

## Features

- Download entire Box shared folders from the terminal
- No API credentials required - works with public shared links
- Supports multiple download methods
- Progress tracking and error handling
- Configurable output directory

## Requirements

- Python 3.7+
- Chrome browser (for Selenium method)
- Required Python packages (see requirements.txt)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd box-folder-downloader

# Install dependencies
pip install -r requirements.txt

# Note: Chrome browser should be installed for Selenium automation
```

## Usage

### Method 1: Selenium Browser Automation (Recommended)

Automated browser-based download that works with most Box shared links:

```bash
# Interactive mode - browser window opens
python box_selenium_downloader.py https://rak.app.box.com/s/your-shared-link

# Headless mode - runs in background
python box_selenium_downloader.py https://rak.app.box.com/s/your-shared-link --headless

# Specify output directory
python box_selenium_downloader.py https://rak.app.box.com/s/your-shared-link --output ./my_downloads
```

### Method 2: Direct API (Limited Support)

Direct API calls without browser (may not work for all shared links):

```bash
# Download from a Box shared link
python box_downloader.py https://rak.app.box.com/s/your-shared-link
```

### Advanced Usage

```bash
# Specify output directory
python box_downloader.py <shared-link> --output ./downloads

# Download only specific file types
python box_downloader.py <shared-link> --filter "*.xlsx"

# Verbose mode
python box_downloader.py <shared-link> --verbose
```

### Using Configuration File

Create a `config.json` file:

```json
{
  "shared_links": [
    "https://rak.app.box.com/s/28k3u2r6xglkx4qh38driemzn3mcj3kq"
  ],
  "output_dir": "downloads",
  "file_types": [".xlsx", ".csv", ".pdf"]
}
```

Then run:

```bash
python box_downloader.py --config config.json
```

## How It Works

The tool uses Box's public API with shared links to:
1. Fetch folder metadata and file listings
2. Generate direct download URLs for each file
3. Download files with progress tracking
4. Handle authentication via shared link headers

## Limitations

- Only works with publicly shared Box links
- Requires "Download" permission on the shared link
- Large files may take time depending on connection speed

## Troubleshooting

**Error: "Could not fetch folder items"**
- Verify the shared link is public and has download permissions
- Check your internet connection
- The shared link may have expired

**Error: "Failed to download file"**
- The file may be too large
- Try downloading with `--verbose` flag for more details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
