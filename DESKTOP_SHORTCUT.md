# Creating Desktop Shortcuts for Projector

This guide shows you how to create a clickable desktop icon for easy launching.

## Method 1: Create macOS Application Bundle (Recommended)

This creates a real macOS app that you can double-click to launch.

### Step 1: Run the App Creator Script

```bash
cd /path/to/webpage_projector
./create_app.sh
```

This creates a `Projector.app` in your project folder.

### Step 2: Use the Application

You now have several options:

**Option A: Keep in Project Folder**
- Double-click `Projector.app` to launch
- Works, but stays in your project folder

**Option B: Move to Applications Folder**
```bash
# Drag the app to Applications, or use command line:
cp -r "Projector.app" /Applications/
```
Now it appears in Launchpad and Spotlight!

**Option C: Add to Dock**
- Drag `Projector.app` to your Dock
- Quick access from anywhere

**Option D: Create Desktop Alias**
- Right-click `Projector.app`
- Select "Make Alias"
- Drag the alias to your Desktop

### First Launch

The first time you open the app, macOS may block it (unsigned app). To fix:

1. **Right-click** the app and choose **Open** (don't double-click)
2. Click **Open** in the dialog
3. Or: System Settings > Privacy & Security > "Open Anyway"

After the first time, you can just double-click normally.

### Troubleshooting

If the app doesn't start:
- Check `~/webpage_projector.log` for error messages
- Make sure you ran `./install.sh` first
- Ensure virtual environment exists in `.venv/`

## Method 2: Simple Desktop Shortcut (AppleScript)

Create a clickable script on your desktop without the full app bundle.

### Step 1: Create AppleScript Application

1. Open **Script Editor** (in Applications > Utilities)

2. Paste this script (replace `/path/to/webpage_projector` with your actual path):

```applescript
-- Projector Launcher
set projectPath to "/Users/billwei/webpage_projector"

tell application "Terminal"
    activate
    do script "cd " & quoted form of projectPath & " && source .venv/bin/activate && python src/main.py"
end tell
```

3. Click **File > Export**
   - Name: `Projector`
   - Where: Desktop (or anywhere you want)
   - File Format: **Application**
   - ✓ Check "Run-only"
   - ✓ Check "Stay open after run handler" (optional)

4. Click **Save**

5. Now you have a clickable app on your desktop!

### Customize the Icon (Optional)

1. Find an icon image you like (PNG, JPG, etc.)
2. Right-click the AppleScript app > **Get Info**
3. Drag your icon image onto the small icon in the top-left of the Info window
4. Close the Info window

## Method 3: Automator Quick Action

Create a macOS Quick Action for even faster launching.

### Step 1: Create Automator Application

1. Open **Automator** (in Applications)

2. Choose **Application** as document type

3. In the search box, type "Run Shell Script"

4. Drag "Run Shell Script" to the workflow area

5. Paste this script (replace path):

```bash
cd /Users/billwei/webpage_projector
source .venv/bin/activate
python src/main.py
```

6. Click **File > Save**
   - Name: `Projector`
   - Where: Desktop (or Applications)

7. Double-click to launch!

## Method 4: Terminal Alias (Power Users)

Add a command to launch from anywhere in Terminal.

### Add to ~/.zshrc (or ~/.bashrc)

```bash
# Open your shell config
nano ~/.zshrc

# Add this line (replace path):
alias projector="cd /Users/billwei/webpage_projector && source .venv/bin/activate && python src/main.py"

# Save (Ctrl+O, Enter, Ctrl+X)

# Reload config
source ~/.zshrc
```

Now you can type `projector` in any Terminal window to launch!

## Comparison of Methods

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **App Bundle** | Native macOS app, works everywhere | Requires `create_app.sh` | Most users |
| **AppleScript** | Easy to create, customizable | Opens Terminal window | Quick setup |
| **Automator** | Clean, no Terminal window | Takes more steps to create | Clean UI preference |
| **Terminal Alias** | Fast for power users | Terminal only | Developers |

## Recommended Setup

For the best experience:

1. **Run `./create_app.sh`** to create the app bundle
2. **Move to Applications**: `cp -r "Projector.app" /Applications/`
3. **Add to Dock**: Drag from Applications to Dock
4. **Create Desktop alias** if you want desktop icon too

This way you can launch from:
- Desktop (alias)
- Dock (quick access)
- Launchpad (searchable)
- Spotlight (type "Projector")

## Adding a Custom Icon

To make your app look professional:

1. **Get an icon** (512x512 PNG recommended)
   - Create one in Preview/Photoshop
   - Or use an icon generator online

2. **Convert to .icns** (macOS icon format)
   - Use online tool: https://cloudconvert.com/png-to-icns
   - Or use Image2Icon app (free on Mac App Store)
   - Or use `iconutil` command (advanced)

3. **Replace the icon**:
   ```bash
   cp your-icon.icns "Projector.app/Contents/Resources/AppIcon.icns"
   ```

4. **Refresh Finder**:
   ```bash
   # Force Finder to update the icon
   touch "Projector.app"
   killall Finder
   ```

## For Distribution

When sharing the app with others:

- Include the `.app` bundle in your distribution
- They can drag it to Applications immediately
- No need to run `create_app.sh` on their machine

**Or** include `create_app.sh` in the distribution and let users create their own app after installation.

## Notes

- The app will always run from the project directory
- Logs are saved to `~/webpage_projector.log` if launched via app bundle
- Terminal window stays open when using AppleScript method
- The app needs `.venv/` to exist (run `./install.sh` first)

## Uninstalling

To remove the app:

```bash
# If in Applications
rm -rf "/Applications/Projector.app"

# If in project folder
rm -rf "Projector.app"

# Remove desktop aliases
# (just drag to Trash)
```