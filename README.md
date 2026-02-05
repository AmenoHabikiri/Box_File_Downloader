<<<<<<< HEAD
# Box_File_Downloader
It is a repository to download the box files/docs from box api.
=======
# Box File Downloader

Automated tool to download files from Box API with Docker support.

## Features

- 📦 Download files from Box folders
- 🔍 Filter files by pattern (e.g., `*.xlsx`, `*.csv`)
- 🕐 Download latest file or all files
- 🐳 Docker support for containerized deployment
- 🔑 Supports both Developer Token and JWT authentication

## Prerequisites

- Node.js 18+ (for local development)
- Docker (for containerized deployment)
- Box API credentials

## Setup

### 1. Get Box API Credentials

#### Option A: Developer Token (Quick Testing)
1. Go to [Box Developer Console](https://app.box.com/developers/console)
2. Create a new app or select existing app
3. Go to "Configuration" tab
4. Scroll down to "Developer Token" section
5. Generate Developer Token
6. Copy the token (valid for 60 minutes)

#### Option B: JWT Authentication (Production)
1. Go to [Box Developer Console](https://app.box.com/developers/console)
2. Create a new app with "Server Authentication (with JWT)"
3. Go to "Configuration" tab
4. Enable "Manage Enterprise Properties"
5. Generate a Public/Private Keypair
6. Download the JSON configuration file as `box_config.json`
7. Submit app for authorization
8. Admin must authorize the app in Box Admin Console

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# For Developer Token (quick testing)
BOX_CLIENT_ID=your_client_id
BOX_CLIENT_SECRET=your_client_secret
BOX_DEVELOPER_TOKEN=your_developer_token

# For JWT (production)
BOX_CLIENT_ID=your_client_id
BOX_CLIENT_SECRET=your_client_secret
BOX_ENTERPRISE_ID=your_enterprise_id
BOX_JWT_CONFIG_PATH=./box_config.json

# Download settings
DOWNLOAD_FOLDER_ID=123456789  # Your Box folder ID
DOWNLOAD_PATH=./downloads
FILE_PATTERN=*.xlsx,*.csv  # Optional: filter files
```

### 4. Find Your Folder ID

1. Open Box in your browser
2. Navigate to the folder you want to download from
3. Look at the URL: `https://app.box.com/folder/123456789`
4. The number `123456789` is your folder ID

## Usage

### Local Development

#### Download all files
```bash
npm run dev
# or
npm run dev all
```

#### Download latest file only
```bash
npm run dev latest
```

#### Download specific file
```bash
npm run dev file "Report_2024.xlsx"
```

### Docker Deployment

#### Build the Docker image
```bash
npm run docker:build
# or
docker build -t box-file-downloader .
```

#### Run with Docker
```bash
npm run docker:run
# or
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/box_config.json:/app/box_config.json:ro \
  box-file-downloader
```

#### Run with Docker Compose
```bash
docker-compose up
```

#### Run as scheduled job (every hour)
Edit `docker-compose.yml` and uncomment the cron command:

```yaml
command: sh -c "while true; do node dist/index.js; sleep 3600; done"
```

Then run:
```bash
docker-compose up -d
```

## Project Structure

```
box-file-downloader/
├── src/
│   ├── index.ts          # Main entry point
│   ├── config.ts         # Configuration loader
│   ├── boxClient.ts      # Box API client
│   └── fileManager.ts    # File download manager
├── downloads/            # Downloaded files (created automatically)
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment template
├── box_config.json       # Box JWT config (not in git)
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── package.json          # Node.js dependencies
├── tsconfig.json         # TypeScript configuration
└── README.md             # This file
```

## Configuration Options

| Variable | Required | Description |
|----------|----------|-------------|
| `BOX_CLIENT_ID` | Yes | Box application client ID |
| `BOX_CLIENT_SECRET` | Yes | Box application client secret |
| `BOX_DEVELOPER_TOKEN` | No* | Developer token (for testing) |
| `BOX_JWT_CONFIG_PATH` | No* | Path to JWT config file (for production) |
| `BOX_ENTERPRISE_ID` | No** | Enterprise ID (required for JWT) |
| `DOWNLOAD_FOLDER_ID` | Yes | Box folder ID to download from |
| `DOWNLOAD_PATH` | No | Local download path (default: `./downloads`) |
| `FILE_PATTERN` | No | File patterns to match (e.g., `*.xlsx,*.csv`) |

\* Either `BOX_DEVELOPER_TOKEN` or `BOX_JWT_CONFIG_PATH` must be provided
\*\* Required when using JWT authentication

## Troubleshooting

### Authentication Errors

**Developer Token expired:**
- Developer tokens expire after 60 minutes
- Generate a new token from Box Developer Console

**JWT authentication failed:**
- Ensure app is authorized by Box Admin
- Check `box_config.json` is in the correct location
- Verify `BOX_ENTERPRISE_ID` matches your enterprise

### Permission Errors

**Cannot access folder:**
- Ensure the Box app has access to the folder
- For JWT apps, content may need to be owned by the Service Account
- Check folder ID is correct

### Download Errors

**No files found:**
- Verify folder ID is correct
- Check file pattern matches your files
- Ensure folder contains files

## License

ISC
>>>>>>> edde7f4 (Initial commit: Box File Downloader automation tool)
