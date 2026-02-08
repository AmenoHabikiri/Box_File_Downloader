#!/usr/bin/env python3
"""
Box Selenium Downloader
Automates browser to download files from Box shared folders.
"""

import argparse
import os
import sys
import time
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Error: Selenium not installed")
    print("Install with: pip install selenium")
    sys.exit(1)


class BoxSeleniumDownloader:
    """Browser automation for downloading Box files."""

    def __init__(self, shared_link, download_dir="downloads", headless=False, verbose=False):
        """
        Initialize Selenium downloader.

        Args:
            shared_link: Box shared folder URL
            download_dir: Directory to save downloaded files
            headless: Run browser in headless mode
            verbose: Enable verbose logging
        """
        self.shared_link = shared_link
        self.download_dir = os.path.abspath(download_dir)
        self.headless = headless
        self.verbose = verbose
        self.driver = None

    def log(self, message, level="info"):
        """Print log message."""
        if self.verbose or level in ["error", "success"]:
            prefix = "✓" if level == "success" else "✗" if level == "error" else "ℹ"
            print(f"{prefix} {message}")

    def setup_driver(self):
        """Setup Chrome WebDriver with download preferences."""
        chrome_options = Options()

        # Set download directory
        os.makedirs(self.download_dir, exist_ok=True)

        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "profile.default_content_settings.popups": 0,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Headless mode
        if self.headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        # Additional options for stability
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            self.log("Starting Chrome browser...", "info")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.log("Browser started successfully", "success")
            return True
        except Exception as e:
            self.log(f"Error starting browser: {e}", "error")
            print("\nTroubleshooting:")
            print("1. Install Chrome browser if not installed")
            print("2. Chrome driver should be auto-downloaded by selenium")
            print("3. Or manually install: brew install chromedriver (macOS)")
            return False

    def wait_for_downloads(self, timeout=60):
        """Wait for all downloads to complete."""
        self.log("Waiting for downloads to complete...", "info")

        end_time = time.time() + timeout
        while time.time() < end_time:
            # Check for .crdownload files (Chrome download in progress)
            downloading = list(Path(self.download_dir).glob("*.crdownload"))
            if not downloading:
                self.log("All downloads completed", "success")
                return True
            time.sleep(1)

        self.log("Download timeout", "error")
        return False

    def download_individual_files(self):
        """Download files one by one using individual download buttons."""
        try:
            self.log("Loading Box shared folder...", "info")
            self.driver.get(self.shared_link)

            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)  # Additional wait for dynamic content

            self.log("Looking for file items...", "info")

            # Try multiple selectors for file items
            file_selectors = [
                "div[role='row']",  # Box uses role='row' for items
                "div.item-row",
                "li[data-item-id]",
                "div[data-testid*='item']",
            ]

            files_found = []
            for selector in file_selectors:
                try:
                    files = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if files:
                        files_found = files
                        self.log(f"Found {len(files)} items using selector: {selector}", "info")
                        break
                except NoSuchElementException:
                    continue

            if not files_found:
                self.log("No files found. Trying alternative method...", "info")
                return self.download_via_actions_menu()

            download_count = 0
            for i, file_item in enumerate(files_found[:20]):  # Limit to first 20 items
                try:
                    # Try to find filename
                    filename = "unknown"
                    try:
                        name_elem = file_item.find_element(By.CSS_SELECTOR, "[class*='name'], [class*='title']")
                        filename = name_elem.text.strip()
                    except:
                        filename = f"file_{i+1}"

                    self.log(f"Processing: {filename}", "info")

                    # Click on the file item to select it
                    try:
                        file_item.click()
                        time.sleep(0.5)
                    except:
                        pass

                    # Look for download button
                    download_selectors = [
                        "button[aria-label*='Download']",
                        "button[data-testid='download-btn']",
                        "button[title*='Download']",
                        "[data-resin-target='download']",
                    ]

                    downloaded = False
                    for selector in download_selectors:
                        try:
                            download_btn = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            download_btn.click()
                            self.log(f"Downloading: {filename}", "success")
                            download_count += 1
                            downloaded = True
                            time.sleep(2)  # Wait between downloads
                            break
                        except (TimeoutException, NoSuchElementException):
                            continue

                    if not downloaded:
                        self.log(f"Could not find download button for: {filename}", "error")

                except Exception as e:
                    self.log(f"Error processing file {i+1}: {e}", "error")
                    continue

            return download_count

        except Exception as e:
            self.log(f"Error in download_individual_files: {e}", "error")
            return 0

    def download_via_actions_menu(self):
        """Try downloading using the Box actions menu."""
        try:
            self.log("Trying actions menu method...", "info")

            # Look for more/actions button
            action_buttons = [
                "button[aria-label='More Options']",
                "button[data-testid='more-options']",
                "button[class*='more-options']",
            ]

            for selector in action_buttons:
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    btn.click()
                    time.sleep(1)

                    # Look for download option in menu
                    download_option = self.driver.find_element(
                        By.XPATH, "//button[contains(., 'Download') or contains(., 'download')]"
                    )
                    download_option.click()
                    self.log("Initiated download via actions menu", "success")
                    time.sleep(3)
                    return 1
                except (NoSuchElementException, TimeoutException):
                    continue

            return 0

        except Exception as e:
            self.log(f"Error in download_via_actions_menu: {e}", "error")
            return 0

    def download_entire_folder(self):
        """Try to download entire folder as zip."""
        try:
            self.log("Looking for 'Download Folder' button...", "info")

            # Selectors for folder download button
            folder_download_selectors = [
                "button[data-testid='download-folder-btn']",
                "button[aria-label*='Download']",
                "//button[contains(text(), 'Download')]",
            ]

            for selector in folder_download_selectors:
                try:
                    if selector.startswith("//"):
                        btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )

                    btn.click()
                    self.log("Downloading entire folder as zip", "success")
                    time.sleep(5)
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue

            self.log("Could not find folder download button", "error")
            return False

        except Exception as e:
            self.log(f"Error downloading folder: {e}", "error")
            return False

    def download_all(self):
        """Main download orchestration."""
        print(f"\n📦 Box Selenium Downloader")
        print(f"{'=' * 60}")
        print(f"Shared Link: {self.shared_link}")
        print(f"Download Directory: {self.download_dir}")
        print(f"Headless Mode: {self.headless}\n")

        # Setup browser
        if not self.setup_driver():
            return False

        try:
            # List files before download
            files_before = set(os.listdir(self.download_dir)) if os.path.exists(self.download_dir) else set()

            # Try folder download first
            self.driver.get(self.shared_link)
            time.sleep(3)

            success = self.download_entire_folder()

            if not success:
                # Fallback to individual file downloads
                self.log("Trying individual file downloads...", "info")
                download_count = self.download_individual_files()
                success = download_count > 0

            # Wait for downloads
            if success:
                self.wait_for_downloads(timeout=120)

            # List downloaded files
            files_after = set(os.listdir(self.download_dir)) if os.path.exists(self.download_dir) else set()
            new_files = files_after - files_before

            print(f"\n{'=' * 60}")
            if new_files:
                print(f"✓ Downloaded {len(new_files)} file(s):")
                for f in sorted(new_files):
                    print(f"  - {f}")
            else:
                print("✗ No files were downloaded")
                print("\nℹ Box may require authentication or has download restrictions")

            print(f"📁 Files saved to: {self.download_dir}\n")

            return len(new_files) > 0

        except Exception as e:
            self.log(f"Error during download: {e}", "error")
            return False

        finally:
            if self.driver:
                if not self.headless:
                    input("\nPress Enter to close browser...")
                self.driver.quit()
                self.log("Browser closed", "info")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Download files from Box shared folders using browser automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://app.box.com/s/abc123
  %(prog)s https://app.box.com/s/abc123 --output ./downloads
  %(prog)s https://app.box.com/s/abc123 --headless
        """
    )

    parser.add_argument('shared_link', help='Box shared folder URL')
    parser.add_argument('-o', '--output', default='downloads',
                       help='Output directory (default: downloads)')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    downloader = BoxSeleniumDownloader(
        args.shared_link,
        args.output,
        args.headless,
        args.verbose
    )

    success = downloader.download_all()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
