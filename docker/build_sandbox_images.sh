#!/bin/bash
# Build VIRA sandbox Docker images with pre-installed dependencies

set -e

echo "Building VIRA Python sandbox image..."
docker build -t vira-python-sandbox:latest -f Dockerfile.python-sandbox .

echo ""
echo "✓ Build complete!"
echo ""
echo "Images built:"
docker images | grep vira-python-sandbox

echo ""
echo "To use in sandbox.py, change line 8 to:"
echo '    "python": "vira-python-sandbox:latest",'
