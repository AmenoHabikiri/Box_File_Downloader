# Usage Examples

## Complete Workflow Examples

### Example 1: Daily Report Download

Download the latest Box reports and keep only the most recent:

```bash
#!/bin/bash
# daily_report_sync.sh

cd /path/to/box-folder-downloader

# Download and cleanup in one command
./download_and_cleanup.sh "https://rak.app.box.com/s/YOUR_LINK"

# The latest report is now available
LATEST_REPORT=$(find extracted_files -name "Data_Volume_Report_*.xlsx" -type f)
echo "Latest report: $LATEST_REPORT"

# Process the report with your analysis script
python /path/to/your/analysis.py "$LATEST_REPORT"
```

### Example 2: Scheduled Automation

Set up a cron job to download reports daily:

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9:00 AM
0 9 * * * cd /Users/yourname/box-folder-downloader && ./download_and_cleanup.sh >> logs/download.log 2>&1
```

### Example 3: Manual Step-by-Step

For more control, run each step separately:

```bash
# Step 1: Download from Box
python box_selenium_downloader.py "BOX_LINK" --headless -v

# Step 2: Extract zip files
unzip -o downloads/*.zip -d extracted_files/

# Step 3: Preview cleanup (dry run)
python cleanup_reports.py extracted_files --dry-run

# Step 4: Actually cleanup
python cleanup_reports.py extracted_files -v

# Step 5: Find and use the latest report
find extracted_files -name "Data_Volume_Report_*.xlsx"
```

### Example 4: Integration with Python Script

```python
#!/usr/bin/env python3
import subprocess
import glob
import pandas as pd

# Download and cleanup
result = subprocess.run([
    './download_and_cleanup.sh',
    'https://rak.app.box.com/s/YOUR_LINK'
], capture_output=True, text=True)

if result.returncode == 0:
    # Find the latest report
    reports = glob.glob('extracted_files/**/Data_Volume_Report_*.xlsx', recursive=True)
    if reports:
        latest_report = reports[0]  # Only one after cleanup

        # Process the Excel file
        df = pd.read_excel(latest_report)
        print(f"Loaded report: {latest_report}")
        print(f"Rows: {len(df)}")

        # Your analysis here
        # ...
else:
    print("Download failed!")
```

### Example 5: Date-Based Processing

Extract the date from the filename and use it:

```bash
#!/bin/bash

# Download and cleanup
./download_and_cleanup.sh

# Get the latest report
REPORT=$(find extracted_files -name "Data_Volume_Report_*.xlsx" -type f)

if [ -f "$REPORT" ]; then
    # Extract date from filename (format: DDMMYYYY)
    BASENAME=$(basename "$REPORT")
    DATE_STR=$(echo "$BASENAME" | grep -oE '[0-9]{8}')

    # Parse date
    DAY=${DATE_STR:0:2}
    MONTH=${DATE_STR:2:2}
    YEAR=${DATE_STR:4:4}

    echo "Report Date: $YEAR-$MONTH-$DAY"
    echo "Processing: $REPORT"

    # Archive with date
    cp "$REPORT" "archive/report_${YEAR}${MONTH}${DAY}.xlsx"
fi
```

### Example 6: Only Cleanup Local Files

If you've already downloaded files and just need cleanup:

```bash
# Preview what will be deleted
python cleanup_reports.py extracted_files --dry-run -v

# Actually delete
python cleanup_reports.py extracted_files -v

# Or clean downloads directory
python cleanup_reports.py downloads -v
```

### Example 7: Notification After Download

Send notification when new report is available:

```bash
#!/bin/bash

# Download and cleanup
./download_and_cleanup.sh "BOX_LINK"

if [ $? -eq 0 ]; then
    REPORT=$(find extracted_files -name "Data_Volume_Report_*.xlsx" -type f)

    # Send email notification (macOS)
    echo "New report downloaded: $REPORT" | mail -s "Box Report Ready" user@example.com

    # Or use osascript for macOS notification
    osascript -e "display notification \"New report downloaded\" with title \"Box Downloader\""
fi
```

### Example 8: Multiple Box Folders

Download from multiple Box folders:

```bash
#!/bin/bash

FOLDERS=(
    "https://rak.app.box.com/s/link1"
    "https://rak.app.box.com/s/link2"
    "https://rak.app.box.com/s/link3"
)

for BOX_LINK in "${FOLDERS[@]}"; do
    echo "Processing: $BOX_LINK"
    ./download_and_cleanup.sh "$BOX_LINK"
    echo ""
done
```

### Example 9: Error Handling

Robust script with error handling:

```bash
#!/bin/bash
set -e  # Exit on error

LOG_FILE="logs/download_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

{
    echo "Starting download at $(date)"

    if ./download_and_cleanup.sh "BOX_LINK"; then
        echo "✓ Download successful"

        # Verify file exists
        REPORT=$(find extracted_files -name "Data_Volume_Report_*.xlsx" -type f)
        if [ -f "$REPORT" ]; then
            echo "✓ Report found: $REPORT"
            SIZE=$(ls -lh "$REPORT" | awk '{print $5}')
            echo "  Size: $SIZE"
        else
            echo "✗ Report not found!"
            exit 1
        fi
    else
        echo "✗ Download failed!"
        exit 1
    fi

    echo "Completed at $(date)"
} 2>&1 | tee "$LOG_FILE"
```

### Example 10: Docker Container

Run in a Docker container for isolation:

```dockerfile
# Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["./download_and_cleanup.sh"]
```

```bash
# Build and run
docker build -t box-downloader .
docker run -v $(pwd)/extracted_files:/app/extracted_files box-downloader
```

## Advanced Scenarios

### Scenario: Weekly Archive

Keep an archive of all weekly reports:

```bash
#!/bin/bash
ARCHIVE_DIR="archive/$(date +%Y/%m)"
mkdir -p "$ARCHIVE_DIR"

# Download latest
./download_and_cleanup.sh

# Copy to archive before cleanup
cp extracted_files/*/Data_Volume_Report_*.xlsx "$ARCHIVE_DIR/" 2>/dev/null || true
```

### Scenario: Compare Reports

Download and compare with previous report:

```python
import pandas as pd
import glob

# Download new report
subprocess.run(['./download_and_cleanup.sh'])

# Load current and previous
current = pd.read_excel('extracted_files/.../Data_Volume_Report_*.xlsx')
previous = pd.read_excel('archive/previous_report.xlsx')

# Compare
diff = current.compare(previous)
print(f"Changes: {len(diff)} rows")
```

## Common Use Cases

### Use Case 1: Data Pipeline Integration

```bash
# Part of your data pipeline
./download_and_cleanup.sh && \
python process_report.py && \
python generate_dashboard.py && \
python send_report.py
```

### Use Case 2: Backup Before Processing

```bash
# Always backup before processing
./download_and_cleanup.sh
cp -r extracted_files backup/$(date +%Y%m%d)/
python process_reports.py extracted_files/
```

### Use Case 3: Git Version Control

```bash
# Track reports in git
./download_and_cleanup.sh
cd extracted_files
git add *.xlsx
git commit -m "Update report $(date +%Y-%m-%d)"
git push
```
