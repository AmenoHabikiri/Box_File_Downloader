import { FileManager } from './fileManager';
import { config } from './config';

async function main() {
  try {
    // Display configuration
    console.log('\n📋 Configuration:');
    console.log(`   Folder ID: ${config.downloadFolderId}`);
    console.log(`   Download Path: ${config.downloadPath}`);
    if (config.filePattern && config.filePattern.length > 0) {
      console.log(`   File Pattern: ${config.filePattern.join(', ')}`);
    }

    // Create file manager
    const fileManager = new FileManager();

    // Parse command line arguments
    const args = process.argv.slice(2);
    const command = args[0] || 'all';

    switch (command) {
      case 'all':
        // Download all files matching pattern
        await fileManager.downloadAllFiles();
        break;

      case 'latest':
        // Download only the latest file
        await fileManager.downloadLatestFile();
        break;

      case 'file':
        // Download specific file by name
        const fileName = args[1];
        if (!fileName) {
          console.error('❌ Please provide a file name');
          console.log('Usage: npm run dev file <filename>');
          process.exit(1);
        }
        await fileManager.downloadFileByName(fileName);
        break;

      default:
        console.log('Usage:');
        console.log('  npm run dev              - Download all files');
        console.log('  npm run dev all          - Download all files');
        console.log('  npm run dev latest       - Download latest file');
        console.log('  npm run dev file <name>  - Download specific file');
        break;
    }

    process.exit(0);
  } catch (error) {
    console.error('\n❌ Fatal error:', error);
    process.exit(1);
  }
}

// Run the application
main();
