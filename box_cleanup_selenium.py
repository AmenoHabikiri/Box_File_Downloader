#!/usr/bin/env python3
"""
Box Selenium Cleanup - Delete old files directly from Box
Requires Box login credentials
"""

import argparse
import os
import sys
import time
import re
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Error: Selenium not installed")
    print("Install with: pip install selenium")
    sys.exit(1)


class BoxCleanupSelenium:
    """Clean up Box folder using browser automation."""

    def __init__(self, shared_link, email=None, password=None, headless=False, verbose=False):
        """
        Initialize Box cleanup.

        Args:
            shared_link: Box shared folder URL
            email: Box login email (optional, for authenticated cleanup)
            password: Box login password (optional)
            headless: Run browser in headless mode
            verbose: Enable verbose logging
        """
        self.shared_link = shared_link
        self.email = email
        self.password = password
        self.headless = headless
        self.verbose = verbose
        self.driver = None

    def log(self, message, level="info"):
        """Print log message."""
        if self.verbose or level in ["error", "success", "action"]:
            prefix = "✓" if level == "success" else "✗" if level == "error" else "→" if level == "action" else "ℹ"
            print(f"{prefix} {message}")

    def parse_date_from_filename(self, filename):
        """Extract date from filename like Data_Volume_Report_07022026.xlsx."""
        pattern = r'Data_Volume_Report_(\d{8})\.xlsx'
        match = re.search(pattern, filename)

        if match:
            date_str = match.group(1)
            try:
                day = int(date_str[0:2])
                month = int(date_str[2:4])
                year = int(date_str[4:8])
                return datetime(year, month, day)
            except ValueError:
                return None
        return None

    def setup_driver(self):
        """Setup Chrome WebDriver."""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        try:
            self.log("Starting Chrome browser...", "info")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            self.log(f"Error starting browser: {e}", "error")
            return False

    def login_to_box(self):
        """Login to Box if credentials provided."""
        if not self.email or not self.password:
            self.log("No credentials provided, skipping login", "info")
            return False

        try:
            self.log("Logging into Box...", "action")
            self.driver.get("https://account.box.com/login")
            time.sleep(2)

            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "login"))
            )
            email_input.send_keys(self.email)

            # Enter password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)

            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            time.sleep(5)  # Wait for login to complete

            self.log("Logged in successfully", "success")
            return True

        except Exception as e:
            self.log(f"Login failed: {e}", "error")
            return False

    def get_files_from_folder(self):
        """Get list of files from Box folder."""
        try:
            self.log("Loading Box folder...", "info")
            self.driver.get(self.shared_link)
            time.sleep(3)

            files = []

            # Try to find file items
            file_items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='row']")

            for item in file_items:
                try:
                    # Get filename
                    name_elem = item.find_element(By.CSS_SELECTOR, "[class*='name']")
                    filename = name_elem.text.strip()

                    if filename and filename != "Name":  # Skip header row
                        files.append({
                            'element': item,
                            'filename': filename,
                            'date': self.parse_date_from_filename(filename)
                        })
                        self.log(f"Found: {filename}", "info")
                except:
                    continue

            return files

        except Exception as e:
            self.log(f"Error getting files: {e}", "error")
            return []

    def delete_file(self, file_element, filename):
        """Delete a file from Box."""
        try:
            # Click on the file to select it
            file_element.click()
            time.sleep(1)

            # Look for delete button or more options
            try:
                # Try direct delete button
                delete_btn = self.driver.find_element(
                    By.CSS_SELECTOR, "button[aria-label*='Delete'], button[data-testid='delete-btn']"
                )
                delete_btn.click()
            except:
                # Try more options menu
                more_btn = self.driver.find_element(
                    By.CSS_SELECTOR, "button[aria-label='More Options']"
                )
                more_btn.click()
                time.sleep(1)

                # Click delete from menu
                delete_option = self.driver.find_element(
                    By.XPATH, "//button[contains(., 'Delete')]"
                )
                delete_option.click()

            time.sleep(1)

            # Confirm deletion if dialog appears
            try:
                confirm_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Delete') or contains(., 'Confirm')]"))
                )
                confirm_btn.click()
                self.log(f"Deleted: {filename}", "success")
                time.sleep(2)
                return True
            except:
                self.log(f"Could not confirm deletion for: {filename}", "error")
                return False

        except Exception as e:
            self.log(f"Error deleting {filename}: {e}", "error")
            return False

    def cleanup_folder(self, dry_run=False):
        """Main cleanup logic."""
        print(f"\n{'=' * 60}")
        print("Box Folder Cleanup (Selenium)")
        print(f"{'=' * 60}")
        print(f"Shared Link: {self.shared_link}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE DELETION'}\n")

        if not self.setup_driver():
            return False

        try:
            # Login if credentials provided
            if self.email:
                if not self.login_to_box():
                    print("\n⚠ Warning: Could not log in. Some operations may fail.")

            # Get files
            files = self.get_files_from_folder()

            if not files:
                print("\n✓ No files found or could not access folder")
                return True

            # Separate Excel files and images
            excel_files = [f for f in files if f['filename'].endswith('.xlsx') or f['filename'].endswith('.xls')]
            image_files = [f for f in files if any(f['filename'].lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg'])]

            # Process Excel files
            excel_with_dates = [f for f in excel_files if f['date']]

            if excel_with_dates:
                # Sort by date
                excel_with_dates.sort(key=lambda x: x['date'], reverse=True)

                latest = excel_with_dates[0]
                print(f"\n→ Keeping latest report:")
                print(f"  {latest['filename']} (Date: {latest['date'].strftime('%Y-%m-%d')})")

                # Delete older reports
                older_files = excel_with_dates[1:]
                if older_files:
                    print(f"\n→ Deleting {len(older_files)} older report(s):")
                    for f in older_files:
                        print(f"  - {f['filename']} (Date: {f['date'].strftime('%Y-%m-%d')})")
                        if not dry_run:
                            self.delete_file(f['element'], f['filename'])

            # Delete images
            if image_files:
                print(f"\n→ Deleting {len(image_files)} image file(s):")
                for f in image_files:
                    print(f"  - {f['filename']}")
                    if not dry_run:
                        self.delete_file(f['element'], f['filename'])

            print(f"\n{'=' * 60}")
            if dry_run:
                print("✓ Dry run complete (no files were deleted)")
            else:
                print("✓ Cleanup complete!")
            print()

            return True

        except Exception as e:
            self.log(f"Error during cleanup: {e}", "error")
            return False

        finally:
            if self.driver:
                if not self.headless and not dry_run:
                    input("\nPress Enter to close browser...")
                self.driver.quit()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Clean up Box folder to keep only the most recent report',
        epilog="""
NOTE: This script requires Box login credentials to delete files.
For local cleanup after download, use cleanup_reports.py instead.

Examples:
  # Dry run (see what would be deleted)
  %(prog)s BOX_LINK --email user@example.com --dry-run

  # Actually delete files
  %(prog)s BOX_LINK --email user@example.com --password PASSWORD
        """
    )

    parser.add_argument('shared_link', help='Box shared folder URL')
    parser.add_argument('--email', help='Box login email')
    parser.add_argument('--password', help='Box login password')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without deleting')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    if not args.dry_run and not args.email:
        print("⚠ Warning: No email provided. Deletion from Box requires login.")
        print("Use --email and --password flags, or --dry-run to test.")
        return 1

    if args.email and not args.password:
        import getpass
        args.password = getpass.getpass("Enter Box password: ")

    cleaner = BoxCleanupSelenium(
        args.shared_link,
        args.email,
        args.password,
        args.headless,
        args.verbose
    )

    success = cleaner.cleanup_folder(args.dry_run)
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
