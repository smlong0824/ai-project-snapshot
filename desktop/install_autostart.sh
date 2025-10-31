#!/usr/bin/env bash
# Install Nova desktop file to user's applications and autostart
set -euo pipefail

# Get the directory where this script lives
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$SRC_DIR/nova.desktop"
REPO_ROOT="$(dirname "$SRC_DIR")"

# Target directories for .desktop file
TARGET_APPS_DIR="$HOME/.local/share/applications"
TARGET_AUTOSTART_DIR="$HOME/.config/autostart"

# Verify Nova repo exists where we expect
if [[ ! -f "$REPO_ROOT/main.py" ]]; then
    echo "❌ Error: main.py not found in $REPO_ROOT"
    echo "The Nova repository may have moved. Please update nova.desktop paths."
    exit 1
fi

# Create target directories if needed
mkdir -p "$TARGET_APPS_DIR" "$TARGET_AUTOSTART_DIR"

# Backup any existing desktop files
for dir in "$TARGET_APPS_DIR" "$TARGET_AUTOSTART_DIR"; do
    if [[ -f "$dir/nova.desktop" ]]; then
        mv "$dir/nova.desktop" "$dir/nova.desktop.bak"
        echo "Backed up existing $dir/nova.desktop"
    fi
done

# Copy and set permissions
cp -f "$DESKTOP_FILE" "$TARGET_APPS_DIR/"
cp -f "$DESKTOP_FILE" "$TARGET_AUTOSTART_DIR/"
chmod 644 "$TARGET_APPS_DIR/$(basename "$DESKTOP_FILE")"
chmod 644 "$TARGET_AUTOSTART_DIR/$(basename "$DESKTOP_FILE")"

echo "✓ Nova desktop icon installed to:"
echo "  $TARGET_APPS_DIR/$(basename "$DESKTOP_FILE")"
echo "  $TARGET_AUTOSTART_DIR/$(basename "$DESKTOP_FILE")"

# Verify python3 is available
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Warning: python3 not found in PATH"
    echo "Please install Python 3 to run Nova:"
    echo "  sudo apt update"
    echo "  sudo apt install python3"
fi

echo "✓ Installation complete"
echo "• The Nova icon should now appear in your applications menu"
echo "• Nova will start automatically when you log in"
echo "• You may need to log out and back in for autostart to take effect"
