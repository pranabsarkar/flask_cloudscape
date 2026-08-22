# Developing and Rebuilding Flask-Cloudscape

This document describes how to compile the React custom elements adapter and rebuild the static JS and CSS bundles for the `flask_cloudscape` Python package.

Standard users installing this package via `pip` **do not** need to follow these steps, as the package contains pre-built assets.

## Prerequisites
- Node.js ≥ 18
- npm ≥ 9
- Access to the `components/` compiler source folder

## Rebuild Instructions

The compilation compiler lives in the `components/` folder sibling to the `flask_cloudscape/` package folder.

1. Navigate to the compiler directory and install dependencies:
   ```bash
   cd components/
   npm install
   ```

2. Run a full build (compiles TypeScript React and bundles JS/CSS into `flask_cloudscape/`):
   ```bash
   ./build.sh
   ```

3. Run a quick bundle-only rebuild (runs esbuild, useful if only modifying the custom elements `adapter.js` file):
   ```bash
   ./build.sh --bundle
   ```

The bundler configuration (`components/esbuild.config.mjs`) automatically outputs the bundled static assets to `flask_cloudscape/flask_cloudscape/static/`.
