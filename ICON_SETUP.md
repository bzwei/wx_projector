# App Icon Setup

The Projector app now has a custom icon!

## Current Setup

✅ **icon.png** - 1024x1024 PNG source image
✅ **icon.icns** - macOS icon file (converted from PNG)
✅ **create_app.sh** - Automatically uses icon.icns when building the app

## How It Works

When you run `./create_app.sh`, the script will:

1. Check if `icon.icns` exists in the project root
2. If found, copy it to the app bundle
3. The app will display your custom icon in Finder, Dock, Launchpad, and Spotlight

## Changing the Icon

To use a different icon:

### Method 1: Replace PNG (Recommended)

1. Replace `icon.png` with your new image (512x512 or larger recommended)
2. Regenerate the .icns file:

```bash
# Create iconset with multiple sizes
mkdir -p /tmp/Projector.iconset
sips -z 16 16     icon.png --out /tmp/Projector.iconset/icon_16x16.png
sips -z 32 32     icon.png --out /tmp/Projector.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out /tmp/Projector.iconset/icon_32x32.png
sips -z 64 64     icon.png --out /tmp/Projector.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out /tmp/Projector.iconset/icon_128x128.png
sips -z 256 256   icon.png --out /tmp/Projector.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out /tmp/Projector.iconset/icon_256x256.png
sips -z 512 512   icon.png --out /tmp/Projector.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out /tmp/Projector.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out /tmp/Projector.iconset/icon_512x512@2x.png

# Convert to .icns
iconutil -c icns /tmp/Projector.iconset -o icon.icns

# Clean up
rm -rf /tmp/Projector.iconset
```

3. Run `./create_app.sh` again to rebuild the app with the new icon

### Method 2: Replace .icns Directly

If you already have a `.icns` file:

```bash
# Replace the icon
cp your-new-icon.icns icon.icns

# Rebuild the app
./create_app.sh
```

### Method 3: Use Online Converter

1. Go to https://cloudconvert.com/png-to-icns
2. Upload your PNG image (512x512 or larger)
3. Download the .icns file
4. Replace `icon.icns` with the downloaded file
5. Run `./create_app.sh`

## Icon Recommendations

### Size
- **Minimum**: 512x512 pixels
- **Recommended**: 1024x1024 pixels
- **Format**: PNG with transparency (for best results)

### Design Tips
- Use simple, clear designs that work at small sizes
- Avoid fine details that won't be visible at 16x16
- Use high contrast for better visibility
- Square aspect ratio works best
- Transparent background is recommended

## Refreshing the Icon

If you rebuild the app but the icon doesn't update:

```bash
# Force macOS to refresh the icon cache
touch "Projector.app"
killall Finder

# Or, delete and rebuild the app
rm -rf "Projector.app"
./create_app.sh
```

## Icon in Distribution

When distributing the app:

- ✅ **Include** `icon.icns` in the repository
- ✅ **Include** `icon.png` in the repository (source file)
- ✅ Users who clone/download will automatically get the icon
- ✅ The icon is embedded in the app bundle when they run `./create_app.sh`

## Viewing the Icon

After running `./create_app.sh`:

- **Finder**: Look at Projector.app - you'll see your custom icon
- **Dock**: Drag the app to the Dock - icon will appear
- **Spotlight**: Search "Projector" - icon shows in results
- **Launchpad**: Icon appears with other apps

## Troubleshooting

### Icon not showing?

1. **Check if icon.icns exists**:
   ```bash
   ls -lh icon.icns
   ```

2. **Rebuild the app**:
   ```bash
   rm -rf "Projector.app"
   ./create_app.sh
   ```

3. **Refresh Finder cache**:
   ```bash
   killall Finder
   ```

4. **Check the app bundle**:
   ```bash
   ls -lh "Projector.app/Contents/Resources/AppIcon.icns"
   ```

### Icon looks blurry?

- Use a higher resolution source image (1024x1024 or larger)
- Ensure the PNG is not upscaled from a smaller image
- Regenerate the .icns file from a high-quality PNG

## Files

- **icon.png**: Source image (1024x1024, 978 KB)
- **icon.icns**: macOS icon bundle (1.9 MB, contains all required sizes)
- Both files are tracked in Git for easy distribution