import esbuild from 'esbuild';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Primary output: standalone flask_cloudscape package (sibling of components/)
const pkgJsDir = path.resolve(__dirname, '../flask_cloudscape/flask_cloudscape/static/js');
const pkgCssDir = path.resolve(__dirname, '../flask_cloudscape/flask_cloudscape/static/css');

// Secondary output: pambify-central static (for backward compatibility)
const flaskJsDir = path.resolve(__dirname, '../pambify-central/src/static/js');
const flaskCssDir = path.resolve(__dirname, '../pambify-central/src/static/css');

// Ensure directories exist
[pkgJsDir, pkgCssDir, flaskJsDir, flaskCssDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

console.log('Bundling Cloudscape adapter with esbuild...');

esbuild.build({
  entryPoints: [path.resolve(__dirname, 'adapter.js')],
  bundle: true,
  minify: true,
  sourcemap: true,
  outfile: path.join(pkgJsDir, 'cloudscape-adapter.js'),
  loader: {
    '.js': 'jsx',
    '.css': 'css',
    '.woff': 'file',
    '.woff2': 'file',
    '.ttf': 'file',
    '.eot': 'file',
    '.svg': 'file'
  },
  define: {
    'process.env.NODE_ENV': '"production"'
  }
}).then(() => {
  console.log('✓ JS bundle created');
  
  // Move CSS next to JS output by esbuild -> pkgCssDir
  const generatedCssPath = path.join(pkgJsDir, 'cloudscape-adapter.css');
  const targetCssPath = path.join(pkgCssDir, 'cloudscape-adapter.css');
  
  if (fs.existsSync(generatedCssPath)) {
    fs.copyFileSync(generatedCssPath, targetCssPath);
    fs.unlinkSync(generatedCssPath);
    console.log('✓ CSS bundle moved to flask_cloudscape/static/css/');
    
    // Move map file too
    const mapSrc = path.join(pkgJsDir, 'cloudscape-adapter.css.map');
    const mapDst = path.join(pkgCssDir, 'cloudscape-adapter.css.map');
    if (fs.existsSync(mapSrc)) {
      fs.copyFileSync(mapSrc, mapDst);
      fs.unlinkSync(mapSrc);
    }
  }

  // Copy to pambify-central for backward compatibility
  const jsBundle = path.join(pkgJsDir, 'cloudscape-adapter.js');
  const jsMap = path.join(pkgJsDir, 'cloudscape-adapter.js.map');
  
  if (fs.existsSync(jsBundle)) {
    fs.copyFileSync(jsBundle, path.join(flaskJsDir, 'cloudscape-adapter.js'));
    console.log('✓ JS copied to pambify-central/src/static/js/');
  }
  if (fs.existsSync(jsMap)) {
    fs.copyFileSync(jsMap, path.join(flaskJsDir, 'cloudscape-adapter.js.map'));
  }
  if (fs.existsSync(targetCssPath)) {
    fs.copyFileSync(targetCssPath, path.join(flaskCssDir, 'cloudscape-adapter.css'));
    console.log('✓ CSS copied to pambify-central/src/static/css/');
    const cssMap = path.join(pkgCssDir, 'cloudscape-adapter.css.map');
    if (fs.existsSync(cssMap)) {
      fs.copyFileSync(cssMap, path.join(flaskCssDir, 'cloudscape-adapter.css.map'));
    }
  }

  console.log('\n✅ Build complete! Assets available in:');
  console.log('   flask_cloudscape/static/js/cloudscape-adapter.js');
  console.log('   flask_cloudscape/static/css/cloudscape-adapter.css');
  console.log('   pambify-central/src/static/js/cloudscape-adapter.js');
  console.log('   pambify-central/src/static/css/cloudscape-adapter.css');
}).catch((err) => {
  console.error('✗ Build failed:', err);
  process.exit(1);
});
