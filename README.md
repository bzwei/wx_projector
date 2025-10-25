# Webpage Projector

Desktop application for projecting Bible verses, hymns, and web content to a secondary display. Built for church presentations.

## Requirements

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- macOS (primary), Windows (supported)
- Dual monitor setup recommended

## Quick Start

### Option 1: Automated Installation (Recommended for macOS)

```bash
# One-step installation
./install.sh

# Run the application
./run.sh
```

That's it! The `install.sh` script will:
- Check Python version (requires 3.12+)
- Install `uv` package manager if needed
- Create virtual environment
- Install all dependencies
- Create default config.json if missing

### Creating a Desktop Shortcut (macOS)

Want to launch with a double-click? Create a macOS app:

```bash
# After installation, create an app bundle
./create_app.sh

# Now you can:
# - Double-click "Projector.app" to launch
# - Drag it to Applications folder
# - Add it to your Dock
# - Create a desktop alias
```

See [DESKTOP_SHORTCUT.md](DESKTOP_SHORTCUT.md) for detailed instructions and other methods.

### Option 2: Manual Installation

#### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Clone and Setup

```bash
# Clone repository
cd webpage_projector

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install core dependencies
uv pip install -e .
```

#### 3. Run the Application

```bash
# Easiest: Use the run script
./run.sh

# Or run using uv (recommended - ensures correct Python version)
uv run python src/main.py

# Or activate venv first, then run
source .venv/bin/activate
python src/main.py
```

## Optional Features

### Google Meet Automation (macOS Only)

The application includes automated Google Meet joining and screen sharing using **macOS native automation** (AppleScript + Accessibility APIs).

**Requirements:**
- macOS only (uses AppleScript and System Events)
- Google Chrome installed
- Accessibility permissions granted to Terminal/your IDE
- **Chrome JavaScript from AppleScript enabled** (optional, for best results)

**Features:**
- Automatically opens meeting URL in Chrome
- Clicks "Join now" button (using JavaScript injection or keyboard fallback)
- Manual screen sharing (automation disabled for reliability)
- No browser automation detection (uses macOS UI automation)

**Important Notes:**
- This is **macOS-specific** and will not work on Windows/Linux
- Requires you to be **already logged into Google** in Chrome
- First time: You may need to grant Accessibility permissions when prompted

**Setup Instructions:**

1. **Grant Accessibility Permissions:**
   - When you first use the feature, macOS will prompt for permissions
   - Go to **System Settings** → **Privacy & Security** → **Accessibility**
   - Enable your Terminal app or IDE (whichever you're running the app from)

2. **Enable JavaScript from AppleScript in Chrome** (Recommended):
   - Open Google Chrome
   - From the menu bar: **View** → **Developer** → **Allow JavaScript from Apple Events**
   - This allows more reliable button clicking
   - **If you skip this**: The app will fall back to keyboard shortcuts (still works!)

**Fallback:**
If automation fails or you're not on macOS, the button will simply open the meeting URL in your default browser for manual joining.

## Development

### Install All Dependencies (including dev tools)

```bash
# Install everything
uv pip install -e ".[dev]"
```

### Project Structure

```
webpage_projector/
├── src/
│   ├── main.py                 # Entry point
│   ├── core/                   # Core functionality
│   │   ├── bible_engine.py     # Bible verse handling
│   │   ├── content_renderer.py # HTML rendering
│   │   └── hymn_repository.py  # Hymn data
│   ├── ui/                     # User interface
│   │   ├── control_panel.py
│   │   ├── projection_window.py
│   │   └── web/                # Web assets (HTML/JS/CSS)
│   └── utils/                  # Utilities
├── books/                      # Bible text files
├── tests/                      # Test files
├── pyproject.toml             # Project configuration
└── config.json                # User configuration
```

### Running Tests

```bash
# Install test dependencies
uv pip install -e ".[dev]"

# Run tests (using uv run)
uv run pytest

# Or activate venv first
source .venv/bin/activate
pytest
```

### Code Quality

```bash
# Format code (using uv run)
uv run black src/

# Lint code (using uv run)
uv run ruff check src/
```

## Configuration

Configuration is stored in `config.json`:

```json
{
    "agenda_slides_id": "your-google-slides-id",
    "bible_font_sizes": {
        "chinese": 28,
        "english": 24
    }
}
```

## Dependencies

### Core (Required)
- **wxPython** (4.2.3+) - GUI framework
- **screeninfo** (0.8.1+) - Multi-monitor detection

### Development
- **pytest** - Testing framework
- **black** - Code formatter
- **ruff** - Fast linter

## Common Commands

```bash
# Install core dependencies only
uv pip install -e .

# Install with development tools
uv pip install -e ".[dev]"

# Update dependencies
uv pip install --upgrade -e .

# Sync dependencies (match pyproject.toml exactly)
uv pip sync

# Run application (using uv run - recommended)
uv run python src/main.py

# Run tests
uv run pytest

# Format and lint code
uv run black src/
uv run ruff check src/
```

## Troubleshooting

### "wx module not found"
```bash
uv pip install wxpython
```

### Virtual environment not activated
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

## Features

- ✅ Bible verse projection with infinite scroll
- ✅ Hymn projection (Google Slides integration)
- ✅ Agenda projection (separate window)
- ✅ Multi-version Bible support (CUV, KJV, etc.)
- ✅ Independent window state management
- ✅ Google Meet automation (macOS only - using AppleScript)
- ✅ Dual monitor support
- ✅ Customizable font sizes
- ✅ Desktop shortcut support (create clickable app icon)

## License

See LICENSE file for details.

## Contributing

This is a church project. Contact the maintainer for contribution guidelines.