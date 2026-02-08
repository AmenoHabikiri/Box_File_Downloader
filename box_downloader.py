#!/usr/bin/env python3
"""
Box Folder Downloader
Download files from Box shared folders without API credentials.
"""

import argparse
import json
import os
import sys
from urllib.parse import urlparse
import requests
from tqdm import tqdm


class BoxDownloader:
    """Handler for downloading files from Box shared folders."""

    def __init__(self, shared_link, output_dir="downloads", verbose=False):
        """
        Initialize Box downloader.

        Args:
            shared_link: Box shared folder URL
            output_dir: Directory to save downloaded files
            verbose: Enable verbose logging
        """
        self.shared_link = shared_link
        self.output_dir = output_dir
        self.verbose = verbose
        self.session = requests.Session()

    def log(self, message, level="info"):
        """Print log message if verbose mode is enabled."""
        if self.verbose or level == "error":
            prefix = "✓" if level == "info" else "✗" if level == "error" else "ℹ"
            print(f"{prefix} {message}")

    def extract_folder_id(self):
        """Extract folder ID from Box shared link."""
        import re
        try:
            # Try to fetch the page and extract folder ID from response
            self.log("Fetching Box page...", "info")
            response = self.session.get(self.shared_link, allow_redirects=True)
            self.log(f"Response status: {response.status_code}", "info")

            if response.status_code == 200:
                # Look for folder ID in the page content
                content = response.text

                # Find folder ID pattern (Box uses typedID with d_ prefix for folders)
                match = re.search(r'"typedID":"d_(\d+)"', content)
                if match:
                    folder_id = match.group(1)
                    self.log(f"Found folder ID: {folder_id}", "info")
                    return folder_id

                # Alternative pattern
                match = re.search(r'"id":"(\d+)".*?"type":"folder"', content, re.DOTALL)
                if match:
                    folder_id = match.group(1)
                    self.log(f"Found folder ID (alt): {folder_id}", "info")
                    return folder_id

                self.log("Could not find folder ID in page content", "error")
            else:
                self.log(f"Failed to fetch page: HTTP {response.status_code}", "error")
        except Exception as e:
            self.log(f"Error extracting folder ID: {e}", "error")
        return None

    def get_folder_items(self, folder_id):
        """
        Fetch items in the Box folder.

        Args:
            folder_id: Box folder ID

        Returns:
            List of file items or None
        """
        api_url = f"https://api.box.com/2.0/folders/{folder_id}/items"

        # Try with BoxApi header format
        headers = {
            "BoxApi": f"shared_link={self.shared_link}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        try:
            response = self.session.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get('entries', [])
            else:
                self.log(f"API method 1 returned status {response.status_code}", "info")

                # Try alternative: extract from webpage
                return self._extract_items_from_webpage()

        except Exception as e:
            self.log(f"Error fetching folder items: {e}", "error")
            # Fallback to webpage extraction
            return self._extract_items_from_webpage()

        return None

    def _extract_items_from_webpage(self):
        """Extract file information directly from the Box webpage."""
        import re
        import json as json_lib

        try:
            self.log("Trying to extract items from webpage...", "info")
            response = self.session.get(self.shared_link, allow_redirects=True)

            if response.status_code != 200:
                return None

            content = response.text

            # Look for JSON data embedded in the page
            # Box embeds file data in a script tag or data attribute
            items = []

            # Try to find the initial data JSON in the page
            json_pattern = r'Box\.postStreamData\s*=\s*({.*?});'
            json_match = re.search(json_pattern, content, re.DOTALL)

            if json_match:
                try:
                    data = json_lib.loads(json_match.group(1))
                    # Navigate the data structure to find files
                    if 'item' in data and 'item_collection' in data['item']:
                        entries = data['item']['item_collection'].get('entries', [])
                        for entry in entries:
                            if entry.get('type') == 'file':
                                items.append({
                                    'id': entry['id'],
                                    'name': entry['name'],
                                    'type': 'file',
                                    'download_url': entry.get('download_url')
                                })
                        self.log(f"Extracted {len(items)} items from embedded JSON", "info")
                        return items if items else None
                except Exception as e:
                    self.log(f"Error parsing embedded JSON: {e}", "info")

            # Fallback: Pattern matching for file entries
            file_pattern = r'"typedID":"f_(\d+)"[^}]*"name":"([^"]+)"'
            matches = re.findall(file_pattern, content)

            for file_id, filename in matches:
                items.append({
                    'id': file_id,
                    'name': filename,
                    'type': 'file'
                })

            self.log(f"Extracted {len(items)} items from webpage", "info")
            return items if items else None

        except Exception as e:
            self.log(f"Error extracting from webpage: {e}", "error")
            return None

    def download_file(self, file_id, filename):
        """
        Download a single file from Box.

        Args:
            file_id: Box file ID
            filename: Name to save the file as

        Returns:
            True if successful, False otherwise
        """
        # Extract shared name from the shared link
        shared_name = self.shared_link.split('/')[-1]

        # Try multiple download URL patterns
        download_urls = [
            # Web download URL (usually works for public shared links)
            f"https://rak.app.box.com/public/static/f_{file_id}.download",
            f"https://rak.app.box.com/shared/static/{shared_name}.download?file_id=f_{file_id}",
            # API endpoint with shared link
            f"https://api.box.com/2.0/files/{file_id}/content",
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": self.shared_link,
        }

        for i, download_url in enumerate(download_urls):
            try:
                self.log(f"Trying download method {i+1}/{len(download_urls)} for {filename}", "info")

                # Add BoxApi header for API endpoint
                if "api.box.com" in download_url:
                    headers["BoxApi"] = f"shared_link={self.shared_link}"

                response = self.session.get(download_url, headers=headers, stream=True, allow_redirects=True)

                if response.status_code == 200:
                    filepath = os.path.join(self.output_dir, filename)
                    total_size = int(response.headers.get('content-length', 0))

                    # Download with progress bar
                    with open(filepath, 'wb') as f:
                        if total_size > 0 and not self.verbose:
                            with tqdm(total=total_size, unit='B', unit_scale=True,
                                    desc=filename) as pbar:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                        else:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                    self.log(f"Downloaded: {filename} using method {i+1}", "info")
                    return True
                else:
                    self.log(f"Method {i+1} returned status {response.status_code}", "info")

            except Exception as e:
                self.log(f"Method {i+1} error: {e}", "info")
                continue

        self.log(f"Failed to download {filename} with all methods", "error")
        return False

    def download_all(self):
        """Download all files from the Box shared folder."""
        print(f"\n📦 Box Folder Downloader")
        print(f"{'=' * 60}")
        print(f"Shared Link: {self.shared_link}")
        print(f"Output Directory: {os.path.abspath(self.output_dir)}\n")

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Extract folder ID
        self.log("Extracting folder ID...", "info")
        folder_id = self.extract_folder_id()

        if not folder_id:
            print("✗ Could not extract folder ID from shared link")
            print("\nℹ Make sure the link is a valid Box shared folder link")
            return False

        self.log(f"Folder ID: {folder_id}", "info")

        # Get folder items
        print("Fetching folder contents...")
        items = self.get_folder_items(folder_id)

        if not items:
            print("✗ Could not fetch folder contents")
            print("\nℹ Possible reasons:")
            print("  - Shared link doesn't have proper permissions")
            print("  - Folder is empty")
            print("  - Network connectivity issues")
            return False

        files = [item for item in items if item.get('type') == 'file']
        print(f"Found {len(files)} file(s)\n")

        # Download each file
        success_count = 0
        for item in files:
            file_id = item['id']
            filename = item['name']
            if self.download_file(file_id, filename):
                success_count += 1

        # Summary
        print(f"\n{'=' * 60}")
        print(f"✓ Downloaded {success_count}/{len(files)} files")
        print(f"📁 Files saved to: {os.path.abspath(self.output_dir)}\n")

        return success_count == len(files)


def load_config(config_file):
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"✗ Error loading config file: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Download files from Box shared folders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://app.box.com/s/abc123
  %(prog)s https://app.box.com/s/abc123 --output ./my_downloads
  %(prog)s --config config.json
        """
    )

    parser.add_argument('shared_link', nargs='?', help='Box shared folder URL')
    parser.add_argument('-o', '--output', default='downloads',
                       help='Output directory (default: downloads)')
    parser.add_argument('-c', '--config', help='Load settings from config file')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    # Handle config file mode
    if args.config:
        config = load_config(args.config)
        shared_links = config.get('shared_links', [])
        output_dir = config.get('output_dir', args.output)

        for link in shared_links:
            downloader = BoxDownloader(link, output_dir, args.verbose)
            downloader.download_all()
        return

    # Handle direct link mode
    if not args.shared_link:
        parser.print_help()
        sys.exit(1)

    downloader = BoxDownloader(args.shared_link, args.output, args.verbose)
    success = downloader.download_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
