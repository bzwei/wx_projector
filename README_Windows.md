# NCF Screen Projector - Windows Edition

A Windows-optimized version of the NCF Screen Projector application built with wxPython, designed specifically for dual-monitor presentation setups.

## Features

### ✅ Implemented Features

- **Bible Verse Projection**: Multi-version Bible projection with support for CUV (Chinese), NIV, and ESV
  - Flexible input parsing (e.g., "John 3:16", "3 16 John", "Genesis 1")
  - Multiple Bible versions displayed side-by-side with color coding
  - Smooth verse navigation with previous/next buttons
  - Chinese and English font size controls
  
- **URL Projection**: Project any website to the second screen
  - Chrome browser integration with automatic positioning
  - Fallback to embedded WebView if Chrome is not available
  - Automatic protocol detection (adds http:// if missing)
  
- **Windows-Specific Optimizations**:
  - Enhanced pywin32 integration for window positioning
  - High-DPI display support
  - Windows 10/11 dark mode title bar support
  - Advanced Chrome window management using Windows API

### 🚧 Partially Implemented Features

- **Google Slides & Hymns Projection**: Framework in place but not yet fully implemented
- **Bible Preview System**: UI elements present but functionality pending
- **Bible History**: Structure ready for implementation
- **Agenda Projection**: Placeholder implementation

## Requirements

Install the required dependencies:

```bash
pip install -r requirements_windows.txt
```

### Dependencies

- **wxpython==4.2.3**: Main GUI framework
- **screeninfo==0.8.1**: Multi-monitor detection
- **pywin32==306**: Windows-specific APIs for enhanced window management

## Installation & Setup

1. **Clone or download** the project files
2. **Install Python 3.9+** if not already installed
3. **Install dependencies**:
   ```bash
   pip install wxpython==4.2.3 screeninfo==0.8.1 pywin32==306
   ```
4. **Prepare Bible files** (optional):
   - Create `books/` directory structure with Bible text files
   - Supported versions: `cuv/`, `niv/`, `esv/`, `kjv/`, `nas/`, `dby/`
   - Format: `books/[version]/vol[XX]/chap[XXX].txt`

## Usage

### Running the Application

```bash
python wx_projector_windows.py
```

### Basic Operations

1. **Bible Projection**:
   - Select Bible versions using checkboxes
   - Adjust font sizes for Chinese and English text
   - Enter verse reference (e.g., "John 3:16")
   - Click "📖 Project" to display on second screen
   - Use ◀/▶ buttons to navigate between verses

2. **URL Projection**:
   - Enter website URL in the URL field
   - Click "🔗 Project" to launch Chrome on second screen
   - Use "👁 Show/Hide" to toggle visibility

3. **Multi-Monitor Setup**:
   - The app automatically detects multiple monitors
   - Projections target the secondary monitor when available
   - Falls back to primary monitor if only one display is detected

## Windows-Specific Features

### Chrome Integration
- Automatic Chrome executable detection
- Advanced window positioning using Windows API
- Fullscreen mode activation with F11 key simulation
- Process monitoring for automatic cleanup

### Enhanced Window Management
- Uses `win32gui` for precise window positioning
- Removes window decorations for fullscreen projection
- Sets windows to topmost layer for reliable display

### UI Optimizations
- Windows 10/11 dark mode compatibility
- High-DPI scaling support
- Native Windows font rendering
- Explicit color management for consistent visibility

## File Structure

```
wx_projector_windows.py    # Main application (Windows optimized)
requirements_windows.txt   # Windows-specific dependencies
README_Windows.md          # This documentation
books/                     # Bible text files (optional)
├── cuv/                   # Chinese Union Version
├── niv/                   # New International Version
├── esv/                   # English Standard Version
└── [other versions]/
```

## Troubleshooting

### Common Issues

1. **pywin32 not working**: 
   - Reinstall: `pip uninstall pywin32 && pip install pywin32==306`
   - Run: `python Scripts/pywin32_postinstall.py -install` (in your Python installation)

2. **Chrome not positioning correctly**:
   - Ensure Chrome is installed and accessible
   - Check Windows permissions for window manipulation
   - Try running as Administrator if issues persist

3. **Text not visible in UI**:
   - The app applies explicit color fixes for Windows
   - Try restarting the application if colors appear incorrect

4. **Bible files not loading**:
   - Ensure `books/` directory structure is correct
   - Check file encoding (CUV should be GB2312, others UTF-8)
   - Verify file naming convention: `vol[XX]/chap[XXX].txt`

## Development Notes

### Architecture
- **MainFrame**: Primary application window with all controls
- **ProjectionFrame**: Fullscreen projection window for secondary display
- **Windows API Integration**: Enhanced window management through pywin32

### Key Classes
- `MainFrame`: Main application window and control logic
- `ProjectionFrame`: Fullscreen projection display
- `WebProjectorApp`: wxPython application wrapper

### Future Enhancements
- Complete Google Slides projection implementation
- Add Bible preview and history features
- Implement hymns database integration
- Add agenda/schedule projection functionality

## License

This is a specialized church projection application optimized for Windows environments.