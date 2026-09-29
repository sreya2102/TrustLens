import fs from 'fs';
import path from 'path';

const srcPath = path.resolve('manifest.json');
const destPath = path.resolve('dist/manifest.json');

try {
  const manifestData = fs.readFileSync(srcPath, 'utf8');
  const manifest = JSON.parse(manifestData);

  // Clean up icon paths for the built version
  // Since Vite copies the contents of public/ directly to the root of dist/
  if (manifest.action && manifest.action.default_icon) {
    for (const key in manifest.action.default_icon) {
      manifest.action.default_icon[key] = manifest.action.default_icon[key].replace('public/', '');
    }
  }
  if (manifest.icons) {
    for (const key in manifest.icons) {
      manifest.icons[key] = manifest.icons[key].replace('public/', '');
    }
  }

  // Ensure dist directory exists
  const destDir = path.dirname(destPath);
  if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
  }

  fs.writeFileSync(destPath, JSON.stringify(manifest, null, 2), 'utf8');
  console.log('Manifest copied and path-optimized for dist/ successfully!');
} catch (error) {
  console.error('Error copying manifest:', error);
  process.exit(1);
}
