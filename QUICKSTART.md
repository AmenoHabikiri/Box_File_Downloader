# Quick Start Guide

## 1. Get Box Developer Token (Fastest Way)

1. Visit: https://app.box.com/developers/console
2. Create or select your app
3. Go to "Configuration" tab
4. Scroll to "Developer Token" section
5. Click "Generate Developer Token"
6. Copy the token (expires in 60 minutes)

## 2. Setup Project

```bash
cd /Users/sagar.tarafdar/Documents/box-file-downloader

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

## 3. Configure .env

Edit `.env` file:

```env
BOX_CLIENT_ID=your_client_id_from_box_console
BOX_CLIENT_SECRET=your_client_secret_from_box_console
BOX_DEVELOPER_TOKEN=your_generated_token_here

DOWNLOAD_FOLDER_ID=123456789  # Get from Box folder URL
DOWNLOAD_PATH=./downloads
FILE_PATTERN=*.xlsx,*.csv
```

**Find Folder ID:**
- Open Box folder in browser
- URL looks like: `https://app.box.com/folder/123456789`
- Use the number `123456789`

## 4. Run

```bash
# Download all files
npm run dev

# Download latest file only
npm run dev latest

# Download specific file
npm run dev file "filename.xlsx"
```

## 5. Docker (Optional)

```bash
# Build
docker build -t box-file-downloader .

# Run
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/downloads:/app/downloads \
  box-file-downloader
```

## Troubleshooting

**"Missing required environment variable"**
- Check all variables in `.env` are filled
- `BOX_CLIENT_ID`, `BOX_CLIENT_SECRET`, `BOX_DEVELOPER_TOKEN`, `DOWNLOAD_FOLDER_ID` are required

**"Authentication failed"**
- Developer token expires in 60 minutes - generate a new one
- Check client ID and secret are correct

**"No files found"**
- Verify folder ID is correct
- Check you have access to the folder in Box
- Try removing `FILE_PATTERN` to see all files

**"Cannot access folder"**
- Make sure your Box app has access to the folder
- Folder must be accessible by the account that created the app
