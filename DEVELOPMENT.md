# Developing and Rebuilding Flask-Cloudscape

This document describes how to compile the React custom elements adapter and rebuild the static JS and CSS bundles for the `flask_cloudscape` Python package.

Standard users installing this package via `pip` **do not** need to follow these steps, as the package contains pre-built assets.

## Prerequisites
- Node.js ≥ 18
- npm ≥ 9
- Access to the `components/` compiler source folder

## Workspace Directory Structure

To compile the assets, your workspace must contain both the compiler folder (`components/`) and the python package folder (`flask_cloudscape/`) side-by-side as siblings:

```text
workspace/
├── components/          # React upstream source and esbuild compiler
└── flask_cloudscape/    # Standalone python package (this repository)
```

## Rebuild Instructions

To rebuild the JS/CSS static assets, navigate to the sibling `components/` directory from this folder:

1. Navigate to the sibling compiler directory and install dependencies:
   ```bash
   cd ../components/
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

The bundler configuration (`components/esbuild.config.mjs`) is set up to automatically compile and write output files directly back into `flask_cloudscape/flask_cloudscape/static/`.
