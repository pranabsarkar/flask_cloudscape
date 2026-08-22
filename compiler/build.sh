#!/usr/bin/env bash
# ============================================================================
# Cloudscape Flask Adapter — Build Script
# ============================================================================
# This script compiles the Cloudscape React components into a bundled JS/CSS
# package that the flask_cloudscape Python extension can serve.
#
# Usage:
#   ./build.sh           # Full build (compile TS + bundle)
#   ./build.sh --bundle  # Bundle only (skip TS compilation, faster)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Cloudscape Flask Adapter — Build Pipeline                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

BUNDLE_ONLY=false
if [[ "${1:-}" == "--bundle" ]]; then
  BUNDLE_ONLY=true
fi

# Step 1: Install npm dependencies (if node_modules missing)
if [ ! -d "node_modules" ]; then
  echo "📦 Installing npm dependencies..."
  npm install
  echo ""
fi

# Step 2: Compile TypeScript + SCSS (quick-build)
if [ "$BUNDLE_ONLY" = false ]; then
  echo "🔨 Running quick-build (TypeScript + SCSS compilation)..."
  npm run quick-build
  echo ""
fi

# Step 3: Bundle with esbuild
echo "📦 Bundling adapter with esbuild..."
node esbuild.config.mjs
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Build complete!                                          ║"
echo "║                                                              ║"
echo "║  Package assets:                                             ║"
echo "║    flask_cloudscape/flask_cloudscape/static/js/cloudscape-adapter.js          ║"
echo "║    flask_cloudscape/flask_cloudscape/static/css/cloudscape-adapter.css        ║"
echo "║                                                              ║"
echo "║  To use in Flask:                                            ║"
echo "║    from flask_cloudscape import Cloudscape                   ║"
echo "║    cloudscape = Cloudscape(app)                              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
