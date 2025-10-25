#!/bin/bash
# Creates a macOS application bundle for Webpage Projector
# Run this after installation to create a clickable app

set -e

APP_NAME="Projector"
BUNDLE_NAME="Projector.app"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "======================================"
echo "Creating macOS Application Bundle"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./install.sh first"
    exit 1
fi

# Create app bundle structure
echo "Creating app bundle structure..."
mkdir -p "$SCRIPT_DIR/$BUNDLE_NAME/Contents/MacOS"
mkdir -p "$SCRIPT_DIR/$BUNDLE_NAME/Contents/Resources"

# Create the launcher script
echo "Creating launcher script..."
cat > "$SCRIPT_DIR/$BUNDLE_NAME/Contents/MacOS/webpage_projector" << 'LAUNCHER_EOF'
#!/bin/bash
# Webpage Projector Launcher

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Go up to the project root (3 levels up from MacOS folder)
PROJECT_DIR="$( cd "$SCRIPT_DIR/../../.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    # Show error in a dialog
    osascript -e 'display dialog "Virtual environment not found. Please run install.sh first." buttons {"OK"} default button "OK" with icon stop with title "Projector"'
    exit 1
fi

# Activate virtual environment and run
source .venv/bin/activate
python src/main.py 2>&1 | tee ~/webpage_projector.log

# If there's an error, show it
if [ $? -ne 0 ]; then
    osascript -e 'display dialog "Application failed to start. Check ~/webpage_projector.log for details." buttons {"OK"} default button "OK" with icon stop with title "Projector"'
fi
LAUNCHER_EOF

chmod +x "$SCRIPT_DIR/$BUNDLE_NAME/Contents/MacOS/webpage_projector"

# Create Info.plist
echo "Creating Info.plist..."
cat > "$SCRIPT_DIR/$BUNDLE_NAME/Contents/Info.plist" << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>webpage_projector</string>
    <key>CFBundleIdentifier</key>
    <string>com.church.webpage-projector</string>
    <key>CFBundleName</key>
    <string>Projector</string>
    <key>CFBundleDisplayName</key>
    <string>Projector</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST_EOF

# Handle app icon
echo "Setting up app icon..."
CUSTOM_ICON="$SCRIPT_DIR/icon.icns"

if [ -f "$CUSTOM_ICON" ]; then
    # Use custom .icns file
    cp "$CUSTOM_ICON" "$SCRIPT_DIR/$BUNDLE_NAME/Contents/Resources/AppIcon.icns"
    echo "✓ Using custom icon: icon.icns"
else
    # No custom icon - create placeholder
    echo "! No custom icon found (icon.icns)"
    echo "  The app will use the default macOS icon"
    touch "$SCRIPT_DIR/$BUNDLE_NAME/Contents/Resources/AppIcon.icns"
fi

echo "✓ App bundle created successfully!"
echo ""
echo "======================================"
echo "Application Ready!"
echo "======================================"
echo ""
echo "The app '$BUNDLE_NAME' has been created in:"
echo "  $SCRIPT_DIR"
echo ""
echo "You can now:"
echo "  1. Double-click '$BUNDLE_NAME' to launch"
echo "  2. Drag it to your Applications folder"
echo "  3. Drag it to your Dock for quick access"
echo "  4. Create a desktop alias (right-click > Make Alias)"
echo ""
echo "Note: The first time you open it, you may need to:"
echo "  - Right-click > Open (to bypass Gatekeeper)"
echo "  - Or: System Settings > Privacy & Security > Open Anyway"
echo ""