import { BoxClient, BoxFile } from './boxClient';
import { config } from './config';

export class FileManager {
  private boxClient: BoxClient;

  constructor() {
    this.boxClient = new BoxClient();
  }

  /**
   * Check if a file matches the configured file patterns
   */
  private matchesPattern(fileName: string): boolean {
    // If no pattern specified, match all files
    if (!config.filePattern || config.filePattern.length === 0) {
      return true;
    }

    // Check if file matches any of the patterns
    return config.filePattern.some(pattern => {
      // Convert wildcard pattern to regex
      const regexPattern = pattern
        .replace(/\./g, '\\.')
        .replace(/\*/g, '.*');
      const regex = new RegExp(`^${regexPattern}$`, 'i');
      return regex.test(fileName);
    });
  }

  /**
   * Download all files from the configured folder
   */
  async downloadAllFiles(): Promise<string[]> {
    console.log('\n========================================');
    console.log('📦 Box File Downloader');
    console.log('========================================\n');

    try {
      // List all files in the folder
      const files = await this.boxClient.listFilesInFolder(config.downloadFolderId);

      if (files.length === 0) {
        console.log('⚠️  No files found in folder');
        return [];
      }

      // Filter files based on pattern
      const filesToDownload = files.filter(file => this.matchesPattern(file.name));

      if (filesToDownload.length === 0) {
        console.log('⚠️  No files match the specified pattern');
        return [];
      }

      console.log(`\n📋 Files to download (${filesToDownload.length}):`);
      filesToDownload.forEach((file, index) => {
        console.log(`   ${index + 1}. ${file.name} (${this.formatFileSize(file.size)})`);
      });

      console.log('\n⬇️  Starting downloads...\n');

      // Download all files
      const downloadedPaths: string[] = [];
      for (const file of filesToDownload) {
        try {
          const filePath = await this.boxClient.downloadFile(
            file.id,
            file.name,
            config.downloadPath
          );
          downloadedPaths.push(filePath);
        } catch (error) {
          console.error(`Failed to download ${file.name}:`, error);
        }
      }

      console.log('\n========================================');
      console.log(`✅ Downloaded ${downloadedPaths.length}/${filesToDownload.length} files`);
      console.log(`📁 Location: ${config.downloadPath}`);
      console.log('========================================\n');

      return downloadedPaths;
    } catch (error) {
      console.error('❌ Error during download process:', error);
      throw error;
    }
  }

  /**
   * Download a specific file by name
   */
  async downloadFileByName(fileName: string): Promise<string | null> {
    console.log(`\n🔍 Looking for file: ${fileName}`);

    try {
      const files = await this.boxClient.listFilesInFolder(config.downloadFolderId);
      const file = files.find(f => f.name === fileName);

      if (!file) {
        console.log(`❌ File not found: ${fileName}`);
        return null;
      }

      const filePath = await this.boxClient.downloadFile(
        file.id,
        file.name,
        config.downloadPath
      );

      return filePath;
    } catch (error) {
      console.error(`❌ Error downloading file ${fileName}:`, error);
      throw error;
    }
  }

  /**
   * Download the latest file from folder
   */
  async downloadLatestFile(): Promise<string | null> {
    console.log('\n🔍 Finding latest file...');

    try {
      const files = await this.boxClient.listFilesInFolder(config.downloadFolderId);

      if (files.length === 0) {
        console.log('⚠️  No files found in folder');
        return null;
      }

      // Filter by pattern
      const matchingFiles = files.filter(file => this.matchesPattern(file.name));

      if (matchingFiles.length === 0) {
        console.log('⚠️  No files match the specified pattern');
        return null;
      }

      // Sort by modified date (most recent first)
      const latestFile = matchingFiles.sort((a, b) => {
        return new Date(b.modified_at).getTime() - new Date(a.modified_at).getTime();
      })[0];

      console.log(`📄 Latest file: ${latestFile.name}`);
      console.log(`📅 Modified: ${latestFile.modified_at}`);

      const filePath = await this.boxClient.downloadFile(
        latestFile.id,
        latestFile.name,
        config.downloadPath
      );

      return filePath;
    } catch (error) {
      console.error('❌ Error downloading latest file:', error);
      throw error;
    }
  }

  /**
   * Format file size for display
   */
  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  }
}
