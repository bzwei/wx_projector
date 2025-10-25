# Quickstart Guide - Development Setup

**Date**: 2025-10-12
**Phase**: 1
**Related**: [plan.md](./plan.md)

## Overview

This guide walks you through setting up the development environment for Webpage Projector and running the application for the first time.

---

## Prerequisites

### Required Software

1. **Python 3.12+**
   ```bash
   python3 --version  # Should show 3.12 or higher
   ```

2. **uv package manager**
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Verify installation
   uv --version
   ```

3. **Git** (for version control)
   ```bash
   git --version
   ```

### Platform-Specific Requirements

**macOS**:
- macOS 12 (Monterey) or later
- Xcode Command Line Tools (for wxPython compilation)
  ```bash
  xcode-select --install
  ```

**Windows**:
- Windows 10 or later
- Microsoft C++ Build Tools (for wxPython)
- Edge WebView2 Runtime (usually pre-installed)

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install python3-dev libgtk-3-dev libwebkit2gtk-4.0-dev
```

---

## Initial Setup

### 1. Clone/Navigate to Repository

```bash
cd /Users/billwei/webpage_projector
```

### 2. Create Virtual Environment

The project already has a virtual environment. Activate it:

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Or create a new one with uv:

```bash
# Create venv
uv venv

# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
# Core dependencies
uv pip install wxPython>=4.2.0
uv pip install screeninfo>=0.8.1

# Development dependencies (optional)
uv pip install pytest>=7.4.0
uv pip install pytest-qt>=4.2.0
uv pip install black>=23.0.0
uv pip install ruff>=0.1.0
```

**Note**: wxPython installation may take 5-10 minutes as it compiles native extensions.

### 4. Verify Installation

```bash
python -c "import wx; print(f'wxPython {wx.version()}')"
python -c "import screeninfo; print(f'screeninfo {screeninfo.__version__}')"
```

Expected output:
```
wxPython 4.2.x
screeninfo 0.8.x
```

---

## Project Structure Setup

### Create Source Directories

```bash
# Navigate to project root
cd /Users/billwei/webpage_projector

# Create source structure
mkdir -p src/ui/components src/ui/styles
mkdir -p src/core src/data src/utils
mkdir -p tests/ui tests/core tests/integration

# Create __init__.py files
touch src/__init__.py
touch src/ui/__init__.py
touch src/ui/components/__init__.py
touch src/ui/styles/__init__.py
touch src/core/__init__.py
touch src/data/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
```

### Verify Data Files

Ensure the following data files exist:

```bash
ls -l books/        # Bible text files
ls -l hymns.csv     # Hymn mappings
ls -l books.csv     # Bible book metadata
```

If missing, you'll see warnings when running the application.

---

## Running the Application

### Phase 2: First Run (UI with Mocks)

Once Phase 2 is implemented, run the control panel:

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or .venv/bin/activate

# Run the application
python src/main.py
```

**Expected Behavior** (Phase 2):
- Control panel window opens (800×900px)
- All sections visible with mock data
- Buttons show "Not implemented" messages
- Status bar shows "Ready to project"

### Phase 3: With Projection Window

After Phase 3 implementation:

```bash
python src/main.py
```

**Expected Behavior** (Phase 3):
- Control panel opens
- Clicking "Project" buttons opens projection window
- Projection window shows mock Bible verses
- Chapter preview panel works with mock data

### Phase 5+: Full Functionality

After Phase 5 implementation:

```bash
python src/main.py
```

**Expected Behavior** (Phase 5+):
- All features working with real data
- Bible verses load from files
- Google Slides projection works
- Multi-monitor detection active

---

## Development Workflow

### 1. Code Style

Use Black for formatting:

```bash
# Format all Python files
black src/ tests/

# Check formatting
black --check src/ tests/
```

Use Ruff for linting:

```bash
# Lint code
ruff check src/ tests/

# Fix auto-fixable issues
ruff check --fix src/ tests/
```

### 2. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/ui/test_main_window.py

# Run with verbose output
pytest -v
```

### 3. Working with Mock Data

During Phases 2-4, mock data is centralized in `src/utils/mock_data.py`:

```python
# Example: Using mock data
from src.utils.mock_data import MOCK_BOOKS, MOCK_VERSES

books = MOCK_BOOKS  # Use mock data
```

### 4. Debugging

Enable wxPython debug output:

```bash
# Run with debug logging
WXDEBUG=1 python src/main.py
```

Enable Python debug logging:

```python
# Add to src/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Common Issues & Solutions

### Issue 1: wxPython Installation Fails

**Error**: `error: command 'gcc' failed`

**Solution**:
- macOS: Install Xcode Command Line Tools: `xcode-select --install`
- Linux: Install build dependencies: `sudo apt-get install python3-dev libgtk-3-dev`
- Windows: Install Microsoft C++ Build Tools

### Issue 2: Import Error for screeninfo

**Error**: `ModuleNotFoundError: No module named 'screeninfo'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install screeninfo
uv pip install screeninfo
```

### Issue 3: Display Detection Not Working

**Error**: No displays detected or incorrect display count

**Solution**:
- Check screeninfo installation: `python -c "from screeninfo import get_monitors; print(get_monitors())"`
- Try disconnecting and reconnecting external displays
- On Linux, ensure X11 or Wayland environment variables are set

### Issue 4: Bible Files Not Found

**Error**: `FileNotFoundError: books/cuv/vol01/chap001.txt`

**Solution**:
```bash
# Verify books directory structure
ls -la books/

# Should see subdirectories: cuv/, kjv/, nas/, niv/, dby/
# Each with vol01/, vol02/, etc. subdirectories
```

### Issue 5: Chinese Text Not Displaying

**Error**: Chinese characters show as boxes or question marks

**Solution**:
- macOS: Chinese fonts are pre-installed (SimHei, Hei)
- Windows: Ensure Microsoft YaHei font is installed
- Linux: Install Chinese fonts: `sudo apt-get install fonts-wqy-zenhei`

---

## Environment Variables

### Optional Configuration

```bash
# Set default display for projection (0 = primary, 1 = secondary)
export WP_TARGET_DISPLAY=1

# Enable debug logging
export WP_DEBUG=1

# Override books directory path
export WP_BOOKS_DIR=/path/to/books

# Override config file path
export WP_CONFIG_PATH=/path/to/config.json
```

---

## IDE Setup

### VS Code

Recommended extensions:
- Python (Microsoft)
- Pylance
- Black Formatter
- Ruff

**settings.json**:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true
}
```

### PyCharm

1. Open project: `/Users/billwei/webpage_projector`
2. Configure interpreter: Settings → Project → Python Interpreter → Add → Existing Environment → Select `venv/bin/python`
3. Enable Black formatter: Settings → Tools → Black → Enable
4. Enable pytest: Settings → Tools → Python Integrated Tools → Default test runner → pytest

---

## Development Phases Checklist

### Phase 2: Static UI - Control Panel
- [ ] `src/main.py` created with wxApp initialization
- [ ] `src/ui/main_window.py` implemented
- [ ] `src/ui/components/url_panel.py` implemented
- [ ] `src/ui/components/slides_panel.py` implemented
- [ ] `src/ui/components/bible_panel.py` implemented
- [ ] `src/ui/styles/theme.py` created with colors/fonts
- [ ] `src/utils/mock_data.py` created with mock data
- [ ] Application runs and shows control panel

### Phase 3: Static UI - Projection Window
- [ ] `src/ui/projection_window.py` implemented
- [ ] `src/ui/components/chapter_preview.py` implemented
- [ ] `src/ui/components/history_panel.py` implemented
- [ ] `src/core/content_renderer.py` implemented (HTML templates)
- [ ] Projection window displays mock Bible content
- [ ] Chapter preview works with mock data
- [ ] Font size controls work

### Phase 4: Display & Validation
- [ ] `src/core/display_manager.py` implemented
- [ ] `src/utils/validators.py` implemented
- [ ] `src/utils/parsers.py` implemented
- [ ] `src/data/slides_repository.py` loads hymns.csv
- [ ] Display detection working
- [ ] Input validation working
- [ ] Book autocomplete working

### Phase 5: Bible Backend
- [ ] `src/data/bible_repository.py` implemented
- [ ] `src/core/bible_engine.py` implemented
- [ ] Bible text loading from files works
- [ ] Multi-version display works
- [ ] Chapter navigation works
- [ ] Progressive verse loading works

### Phase 6: Slides & Web
- [ ] WebView integration in projection window
- [ ] Google Slides projection works
- [ ] URL projection works
- [ ] Show/Hide toggle works
- [ ] Fullscreen mode works

### Phase 7: Config & History
- [ ] `src/core/history_manager.py` implemented
- [ ] `src/data/config_manager.py` implemented
- [ ] History tracking works
- [ ] Settings persistence works
- [ ] Keyboard shortcuts work

---

## Testing Checklist

### Manual Testing (After Each Phase)

**Phase 2**:
- [ ] Control panel opens and displays correctly
- [ ] All sections visible with proper spacing
- [ ] Window is exactly 800×900px
- [ ] Buttons are clickable (even if showing placeholders)

**Phase 3**:
- [ ] Projection window opens
- [ ] Mock Bible verses display correctly
- [ ] Chapter preview shows mock verses
- [ ] Font size controls change text size
- [ ] History dropdown shows mock entries

**Phase 4**:
- [ ] Status bar shows real display count
- [ ] Invalid verse references show errors
- [ ] Book autocomplete suggests books
- [ ] Hymn ID validation works

**Phase 5**:
- [ ] Real Bible verses load and display
- [ ] Multiple versions display correctly
- [ ] Chapter navigation works
- [ ] Verse navigation works

**Phase 6**:
- [ ] Google Slides open in presentation mode
- [ ] URLs project correctly
- [ ] Fullscreen works on secondary display
- [ ] Show/Hide toggle works

**Phase 7**:
- [ ] History tracks projections
- [ ] Settings save and restore
- [ ] Keyboard shortcuts work
- [ ] Clear history works

---

## Useful Commands

```bash
# Start fresh (remove all .pyc files)
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# List installed packages
uv pip list

# Update all packages
uv pip install --upgrade wxPython screeninfo

# Run application with error logging
python src/main.py 2>&1 | tee app.log

# Run tests with verbose output
pytest -vv -s

# Generate test coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
```

---

## Next Steps

1. **Complete Phase 0**: Review [research.md](./research.md) for UX decisions
2. **Review Phase 1**: Check [data-model.md](./data-model.md) and [contracts/component-interfaces.md](./contracts/component-interfaces.md)
3. **Start Phase 2**: Begin implementing control panel UI with mock data
4. **Iterate**: Build incrementally, test frequently, validate UX early

---

## Resources

### Documentation
- **wxPython Docs**: https://docs.wxpython.org/
- **screeninfo**: https://github.com/rr-/screeninfo
- **Python Dataclasses**: https://docs.python.org/3/library/dataclasses.html

### Similar Projects
- **OpenLP**: https://openlp.org/ (open-source worship software)
- **ProPresenter**: https://renewedvision.com/propresenter/ (commercial reference)

### Support
- **Project Issues**: Create issue in repository
- **wxPython Forum**: https://discuss.wxpython.org/
- **Python Discord**: https://discord.gg/python

---

**Ready to Start!** Proceed to Phase 2 implementation when ready.