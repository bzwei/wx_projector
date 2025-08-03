# Web Page Projector

A Python desktop application that displays web pages on a second screen in fullscreen mode without borders.

## Features

- Simple GUI with URL input
- Automatic detection of multiple monitors
- Fullscreen projection on second screen
- Borderless display for clean presentation
- URL validation and formatting
- Easy start/stop projection controls
- **Enhanced Google Slides support with hymn lookup**
- CSV-based hymn database with autocomplete
- Smart textbox that recognizes hymn names and Slides IDs

## Requirements

- Python 3.7 or higher
- Two monitors (recommended, but works with single monitor)
- macOS, Windows, or Linux

## Installation

1. Clone or download this project
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python wx_projector.py
```

Or use the original tkinter version:

```bash
python native_projector.py
```

2. Enter a URL in the text box (protocol http:// or https:// is optional)
3. Click "Project to Second Screen" or press Enter
4. The webpage will open in fullscreen mode on your second monitor
5. Click "Stop Projection" to close the projected window

## Supported URL Formats

- `google.com` (automatically becomes `https://google.com`)
- `http://example.com`
- `https://www.example.com`
- `localhost:3000`
- `192.168.1.100:8080`

## Keyboard Shortcuts

- **Enter**: Start projection (when URL field is focused)
- **ESC**: Close projection window (when projection window is focused)

## Monitor Detection

The application automatically detects available monitors:
- With 2+ monitors: Projects to the second monitor
- With 1 monitor: Projects to the primary monitor
- Shows monitor count in the interface

## Dependencies

- `wxpython`: For native GUI and web content display
- `screeninfo`: For multi-monitor detection

## Hymn Database Setup

The application expects a `hymns.csv` file in the project directory with two columns:
1. **Hymn ID**: Numeric ID (e.g., "123") or letter + numeric (e.g., "A123", "C456")
2. **Google Slides ID**: The corresponding Google Slides presentation ID

Example `hymns.csv`:
```csv
Hymn ID,Google Slides ID
123,1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
A456,1Abc123DefGhIjKlMnOpQrStUvWxYz456789AbCdEf
C789,1XyZ987WvUtSrQpOnMlKjIhGfEdCbA654321ZyXwVu
```

### Using the Hymn Lookup Feature

1. **Enter Hymn ID**: Type a hymn ID (e.g., "123", "A456", "C789")
2. **ID Recognition**: The app detects valid hymn IDs and shows the associated Slides ID
3. **Browse by Category**: Click the 🎵 button to browse hymns organized by:
   - Numeric IDs (123, 456, etc.)
   - A-Series (A123, A456, etc.)  
   - C-Series (C123, C456, etc.)
4. **Direct Entry**: You can still enter Google Slides IDs or URLs directly
5. **Auto-lookup**: Hymn IDs are automatically converted to Slides URLs for presentation

## Troubleshooting

### "No module named 'wx'" Error
Install the wxPython dependency:
```bash
pip install wxpython
```

### Windows-Specific Setup
For enhanced Windows support with better fullscreen handling:
```bash
pip install -r requirements_windows.txt
```
Then run the Windows-optimized version:
```bash
python wx_projector_windows.py
```

### Projection Window Not Appearing
- Check that the URL is valid and accessible
- Ensure the target website allows embedding
- Try a different URL (some sites block iframe embedding)

### Single Monitor Setup
The app works with a single monitor but is designed for dual-monitor setups. With one monitor, the projection will appear on your primary screen.

## Platform-Specific Notes

### macOS
- May require allowing Python to control your computer in System Preferences > Security & Privacy > Privacy > Accessibility

### Windows
- Works with Windows 10/11
- Multiple monitor detection should work automatically
- For best results, use the Windows-optimized version (`wx_projector_windows.py`)
- Supports Edge WebView2 for modern web standards
- Enhanced fullscreen handling for Windows display scaling

### Linux
- Requires X11 or Wayland
- May need additional packages depending on your distribution

## License

This project is open source and available under the MIT License.
