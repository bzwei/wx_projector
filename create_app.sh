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

# Redirect all output to log file
exec >> ~/webpage_projector_launch.log 2>&1
echo "=== Launch attempt at $(date) ==="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script directory: $SCRIPT_DIR"

# Go up to the project root (3 levels up from MacOS folder)
PROJECT_DIR="$( cd "$SCRIPT_DIR/../../.." && pwd )"
echo "Project directory: $PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR" || {
    osascript -e 'display dialog "Failed to change to project directory" buttons {"OK"} default button "OK" with icon stop with title "Projector"'
    exit 1
}

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found at $PROJECT_DIR/.venv"
    osascript -e 'display dialog "Virtual environment not found. Please run install.sh first." buttons {"OK"} default button "OK" with icon stop with title "Projector"'
    exit 1
fi

echo "Virtual environment found"
echo "Activating virtual environment..."
source .venv/bin/activate

echo "Launching Python application..."
# Run in background so the launcher can exit
python src/main.py >> ~/webpage_projector.log 2>&1 &

# Give it a moment to start
sleep 1

# Check if it's still running
if ps -p $! > /dev/null; then
    echo "Application started successfully (PID: $!)"
    exit 0
else
    echo "ERROR: Application failed to start"
    osascript -e 'display dialog "Application failed to start. Check ~/webpage_projector.log for details." buttons {"OK"} default button "OK" with icon stop with title "Projector"'
    exit 1
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
echo "IMPORTANT: Keep '$BUNDLE_NAME' in this directory!"
echo "  The app needs to stay here to access the Python environment."
echo ""
echo "You can now:"
echo "  1. Double-click '$BUNDLE_NAME' to launch"
echo "  2. Drag it to your Dock for quick access"
echo "  3. Create an alias:"
echo "       Right-click '$BUNDLE_NAME' > Make Alias"
echo "       Then move the alias to Applications or Desktop"
echo ""
echo "Or run this command to create an alias in Applications:"
echo "  ln -s \"$SCRIPT_DIR/$BUNDLE_NAME\" ~/Applications/"
echo ""
echo "Note: The first time you open it, you may need to:"
echo "  - Right-click > Open (to bypass Gatekeeper)"
echo "  - Or: System Settings > Privacy & Security > Open Anyway"
echo ""