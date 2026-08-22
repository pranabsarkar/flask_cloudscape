# Developing and Rebuilding Flask-Cloudscape

This document describes how to compile the React custom elements adapter and rebuild the static JS and CSS bundles for the `flask_cloudscape` Python package.

Standard users installing this package via `pip` **do not** need to follow these steps, as the package contains pre-built assets.

> [!IMPORTANT]
> If you only want to install and use the `flask-cloudscape` package in your Flask app, **skip this document**. You do **not** need to set up this compiler environment or clone the AWS components repository.

## Prerequisites
- Node.js ≥ 18
- npm ≥ 9
- The official Cloudscape source code repository

## Setting Up the Compiler

If you wish to modify the React adapter or rebuild the assets, follow these steps to set up the build environment:

1. Clone the official AWS Cloudscape components repository as a sibling to this repository:
   ```bash
   # Navigate to the parent directory of this repository
   cd ..

   # Clone the official repository (creates a 'components' directory next to flask_cloudscape)
   git clone https://github.com/cloudscape-design/components.git
   ```

2. Copy the adapter wrapper and build files from the `compiler/` folder of this repository into the cloned `components/` folder:
   ```bash
   # From the root of this flask_cloudscape repository, run:
   cp -r compiler/* ../components/
   ```

## Workspace Directory Structure

Once set up, your workspace must look like this:

```text
workspace/
├── components/          # Cloned AWS source + copied compiler/ files
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
