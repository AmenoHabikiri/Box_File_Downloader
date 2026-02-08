#!/usr/bin/env python3
"""
Box Report Cleanup Utility
Keeps only the most recent Data_Volume_Report file and removes images.
"""

import os
import re
import argparse
from datetime import datetime
from pathlib import Path


class ReportCleaner:
    """Cleans up Box downloads to keep only the most recent report."""

    def __init__(self, directory, dry_run=False, verbose=False):
        """
        Initialize report cleaner.

        Args:
            directory: Directory containing downloaded files
            dry_run: If True, only show what would be deleted
            verbose: Enable verbose output
        """
        self.directory = directory
        self.dry_run = dry_run
        self.verbose = verbose

    def log(self, message, level="info"):
        """Print log message."""
        if self.verbose or level in ["error", "success", "action"]:
            prefix = "✓" if level == "success" else "✗" if level == "error" else "→" if level == "action" else "ℹ"
            print(f"{prefix} {message}")

    def parse_date_from_filename(self, filename):
        """
        Extract date from filename like Data_Volume_Report_07022026.xlsx.

        Args:
            filename: Filename to parse

        Returns:
            datetime object or None
        """
        # Pattern: Data_Volume_Report_DDMMYYYY.xlsx
        pattern = r'Data_Volume_Report_(\d{8})\.xlsx'
        match = re.search(pattern, filename)

        if match:
            date_str = match.group(1)
            # Parse as DDMMYYYY
            try:
                day = int(date_str[0:2])
                month = int(date_str[2:4])
                year = int(date_str[4:8])
                return datetime(year, month, day)
            except ValueError as e:
                self.log(f"Invalid date in filename {filename}: {e}", "error")
                return None

        return None

    def find_excel_files(self):
        """
        Find all Excel files with date patterns.

        Returns:
            List of tuples (filepath, date)
        """
        excel_files = []

        for root, dirs, files in os.walk(self.directory):
            for filename in files:
                if filename.endswith('.xlsx') or filename.endswith('.xls'):
                    filepath = os.path.join(root, filename)
                    date = self.parse_date_from_filename(filename)

                    if date:
                        excel_files.append((filepath, date, filename))
                        self.log(f"Found report: {filename} (Date: {date.strftime('%Y-%m-%d')})", "info")

        return excel_files

    def find_image_files(self):
        """
        Find all image files (PNG, JPG, etc.).

        Returns:
            List of image file paths
        """
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        image_files = []

        for root, dirs, files in os.walk(self.directory):
            for filename in files:
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    filepath = os.path.join(root, filename)
                    image_files.append(filepath)
                    self.log(f"Found image: {filename}", "info")

        return image_files

    def clean_directory(self):
        """
        Main cleanup logic: keep only the most recent report, delete images.

        Returns:
            Tuple (kept_file, deleted_files)
        """
        print(f"\n{'=' * 60}")
        print("Box Report Cleanup Utility")
        print(f"{'=' * 60}")
        print(f"Directory: {os.path.abspath(self.directory)}")
        print(f"Mode: {'DRY RUN (no files will be deleted)' if self.dry_run else 'LIVE (files will be deleted)'}\n")

        # Find Excel files
        excel_files = self.find_excel_files()

        if not excel_files:
            print("\n✓ No Data_Volume_Report files found")
            kept_file = None
        elif len(excel_files) == 1:
            print(f"\n✓ Only one report file found: {excel_files[0][2]}")
            print("  No cleanup needed")
            kept_file = excel_files[0][0]
        else:
            # Sort by date (most recent first)
            excel_files.sort(key=lambda x: x[1], reverse=True)

            kept_file = excel_files[0][0]
            kept_filename = excel_files[0][2]
            kept_date = excel_files[0][1]

            print(f"\n→ Keeping most recent report:")
            print(f"  File: {kept_filename}")
            print(f"  Date: {kept_date.strftime('%Y-%m-%d (%A)')}")

            # Delete older files
            files_to_delete = excel_files[1:]
            if files_to_delete:
                print(f"\n→ Deleting {len(files_to_delete)} older report(s):")
                for filepath, date, filename in files_to_delete:
                    print(f"  - {filename} (Date: {date.strftime('%Y-%m-%d')})")
                    if not self.dry_run:
                        try:
                            os.remove(filepath)
                            self.log(f"Deleted: {filename}", "success")
                        except Exception as e:
                            self.log(f"Error deleting {filename}: {e}", "error")
                    else:
                        self.log(f"Would delete: {filename}", "action")

        # Find and delete image files
        image_files = self.find_image_files()
        if image_files:
            print(f"\n→ Deleting {len(image_files)} image file(s):")
            for filepath in image_files:
                filename = os.path.basename(filepath)
                print(f"  - {filename}")
                if not self.dry_run:
                    try:
                        os.remove(filepath)
                        self.log(f"Deleted: {filename}", "success")
                    except Exception as e:
                        self.log(f"Error deleting {filename}: {e}", "error")
                else:
                    self.log(f"Would delete: {filename}", "action")
        else:
            print("\n✓ No image files found")

        # Summary
        print(f"\n{'=' * 60}")
        if not self.dry_run:
            print("✓ Cleanup complete!")
        else:
            print("✓ Dry run complete (no files were deleted)")

        if kept_file:
            print(f"📄 Latest report: {os.path.basename(kept_file)}")
            print(f"📁 Location: {kept_file}")
        print()

        return kept_file, len(excel_files) - 1 + len(image_files) if excel_files else len(image_files)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Clean up Box downloads to keep only the most recent report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview what would be deleted)
  %(prog)s extracted_files --dry-run

  # Actually delete files
  %(prog)s extracted_files

  # Clean downloads directory
  %(prog)s downloads --verbose

  # Clean specific folder
  %(prog)s "extracted_files/Radcom Daily HealthCheck Report"
        """
    )

    parser.add_argument('directory', nargs='?', default='extracted_files',
                       help='Directory to clean (default: extracted_files)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"✗ Error: Directory not found: {args.directory}")
        return 1

    cleaner = ReportCleaner(args.directory, args.dry_run, args.verbose)
    kept_file, deleted_count = cleaner.clean_directory()

    return 0


if __name__ == '__main__':
    exit(main())
