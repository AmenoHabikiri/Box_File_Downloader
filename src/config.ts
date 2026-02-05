import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config();

export interface Config {
  // Box API credentials
  boxClientId: string;
  boxClientSecret: string;
  boxEnterpriseId?: string;
  boxDeveloperToken?: string;
  boxJwtConfigPath?: string;

  // Download configuration
  downloadFolderId: string;
  downloadPath: string;
  filePattern?: string[];
}

function getEnvVar(key: string, required: boolean = false): string | undefined {
  const value = process.env[key];

  if (required && !value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }

  return value;
}

export function loadConfig(): Config {
  const config: Config = {
    boxClientId: getEnvVar('BOX_CLIENT_ID', true)!,
    boxClientSecret: getEnvVar('BOX_CLIENT_SECRET', true)!,
    boxEnterpriseId: getEnvVar('BOX_ENTERPRISE_ID'),
    boxDeveloperToken: getEnvVar('BOX_DEVELOPER_TOKEN'),
    boxJwtConfigPath: getEnvVar('BOX_JWT_CONFIG_PATH'),

    downloadFolderId: getEnvVar('DOWNLOAD_FOLDER_ID', true)!,
    downloadPath: getEnvVar('DOWNLOAD_PATH') || './downloads',
    filePattern: getEnvVar('FILE_PATTERN')?.split(',').map(p => p.trim())
  };

  // Validate authentication method
  if (!config.boxDeveloperToken && !config.boxJwtConfigPath) {
    throw new Error('Either BOX_DEVELOPER_TOKEN or BOX_JWT_CONFIG_PATH must be provided');
  }

  return config;
}

export const config = loadConfig();
