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

# Setup logging directory
LOG_DIR="$HOME/Library/Logs/Projector"
mkdir -p "$LOG_DIR"

# Log launcher activity (lightweight)
{
    echo "=== $(date) ==="
    echo "Launching from: $PROJECT_DIR"
} >> "$LOG_DIR/launch.log"

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "ERROR: Failed to cd to $PROJECT_DIR" >> "$LOG_DIR/launch.log"
    osascript -e 'display dialog "Failed to change to project directory" buttons {"OK"} default button "OK" with icon stop with title "Projector"'
    exit 1
}

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found" >> "$LOG_DIR/launch.log"
    osascript -e 'display dialog "Virtual environment not found. Please run install.sh first." buttons {"OK"} default button "OK" with icon stop with title "Projector"'
    exit 1
fi

# Activate and launch
source .venv/bin/activate

# Launch in background, redirect output to log
.venv/bin/python src/main.py >> "$LOG_DIR/app.log" 2>&1 &
APP_PID=$!

# Give it a moment to start
sleep 1

# Verify it started
if ps -p $APP_PID > /dev/null; then
    echo "Started successfully (PID: $APP_PID)" >> "$LOG_DIR/launch.log"
    exit 0
else
    echo "ERROR: Failed to start" >> "$LOG_DIR/launch.log"
    osascript -e 'display dialog "Application failed to start. Check logs in ~/Library/Logs/Projector/" buttons {"OK"} default button "OK" with icon stop with title "Projector"'
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
    <key>LSArchitecturePriority</key>
    <array>
        <string>arm64</string>
        <string>x86_64</string>
    </array>
    <key>LSRequiresNativeExecution</key>
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