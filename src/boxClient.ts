import BoxSDK from 'box-node-sdk';
import fs from 'fs';
import path from 'path';
import { config } from './config';

export interface BoxFile {
  id: string;
  name: string;
  size: number;
  modified_at: string;
}

export class BoxClient {
  private sdk: BoxSDK;
  private client: any;

  constructor() {
    this.sdk = new BoxSDK({
      clientID: config.boxClientId,
      clientSecret: config.boxClientSecret
    });

    this.initializeClient();
  }

  private initializeClient(): void {
    if (config.boxDeveloperToken) {
      // Use Developer Token for quick testing
      console.log('🔑 Authenticating with Developer Token...');
      this.client = this.sdk.getBasicClient(config.boxDeveloperToken);
    } else if (config.boxJwtConfigPath) {
      // Use JWT for production
      console.log('🔑 Authenticating with JWT...');
      const jwtConfig = JSON.parse(fs.readFileSync(config.boxJwtConfigPath, 'utf8'));
      this.sdk = BoxSDK.getPreconfiguredInstance(jwtConfig);
      this.client = this.sdk.getAppAuthClient('enterprise', config.boxEnterpriseId);
    } else {
      throw new Error('No authentication method configured');
    }
  }

  /**
   * List all files in a folder
   */
  async listFilesInFolder(folderId: string): Promise<BoxFile[]> {
    try {
      console.log(`📂 Fetching files from folder: ${folderId}`);

      const items = await this.client.folders.getItems(folderId, {
        fields: 'id,name,size,modified_at,type'
      });

      // Filter only files (not folders)
      const files = items.entries
        .filter((item: any) => item.type === 'file')
        .map((file: any) => ({
          id: file.id,
          name: file.name,
          size: file.size,
          modified_at: file.modified_at
        }));

      console.log(`✅ Found ${files.length} files`);
      return files;
    } catch (error) {
      console.error('❌ Error listing files:', error);
      throw error;
    }
  }

  /**
   * Download a file from Box
   */
  async downloadFile(fileId: string, fileName: string, downloadPath: string): Promise<string> {
    try {
      // Ensure download directory exists
      if (!fs.existsSync(downloadPath)) {
        fs.mkdirSync(downloadPath, { recursive: true });
      }

      const filePath = path.join(downloadPath, fileName);
      const writeStream = fs.createWriteStream(filePath);

      console.log(`⬇️  Downloading: ${fileName}`);

      return new Promise((resolve, reject) => {
        this.client.files.getReadStream(fileId, null, (error: Error, stream: any) => {
          if (error) {
            reject(error);
            return;
          }

          stream.pipe(writeStream);

          writeStream.on('finish', () => {
            console.log(`✅ Downloaded: ${fileName}`);
            resolve(filePath);
          });

          writeStream.on('error', (err: Error) => {
            reject(err);
          });
        });
      });
    } catch (error) {
      console.error(`❌ Error downloading file ${fileName}:`, error);
      throw error;
    }
  }

  /**
   * Get file information
   */
  async getFileInfo(fileId: string): Promise<any> {
    try {
      const file = await this.client.files.get(fileId);
      return file;
    } catch (error) {
      console.error(`❌ Error getting file info for ${fileId}:`, error);
      throw error;
    }
  }

  /**
   * Search for files in Box
   */
  async searchFiles(query: string, folderId?: string): Promise<BoxFile[]> {
    try {
      console.log(`🔍 Searching for: ${query}`);

      const options: any = {
        query: query,
        type: 'file',
        fields: 'id,name,size,modified_at'
      };

      if (folderId) {
        options.ancestor_folder_ids = folderId;
      }

      const results = await this.client.search.query(options);

      const files = results.entries.map((file: any) => ({
        id: file.id,
        name: file.name,
        size: file.size,
        modified_at: file.modified_at
      }));

      console.log(`✅ Found ${files.length} matching files`);
      return files;
    } catch (error) {
      console.error('❌ Error searching files:', error);
      throw error;
    }
  }
}
