#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Set up / activate venv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Building app..."
pyinstaller \
    --windowed \
    --name "DAW Project Browser" \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --hidden-import=webview \
    --hidden-import=webview.platforms.cocoa \
    --hidden-import=flask \
    --hidden-import=werkzeug \
    --hidden-import=jinja2 \
    --noconfirm \
    app.py

echo ""
echo "Done! App bundle is at: dist/DAW Project Browser.app"
echo "To distribute, zip the .app or copy it to /Applications."
