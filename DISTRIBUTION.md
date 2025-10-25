# Distribution Guide for Webpage Projector

This guide explains how to distribute and install this application on another Mac machine.

## What You Need to Share

To run this application on another Mac, you need to share the following files/folders:

### Required Files and Folders

1. **Source Code** (`src/` directory)
   - Contains all application code

2. **Configuration Files**
   - `pyproject.toml` - Project dependencies and metadata
   - `uv.lock` - Locked dependency versions (ensures consistency)
   - `books.csv` - Bible book metadata
   - `hymns.csv` - Hymn data

3. **Data Files**
   - `books/` directory - Bible text files (all versions)
   - `ncf_background.png` - Background image for projection

4. **Installation Scripts**
   - `install.sh` - Automated installation script
   - `run.sh` - Simple run script
   - `README.md` - User documentation

5. **Optional Files**
   - `config.json` - User preferences (will be auto-generated if missing)

### Files/Folders to EXCLUDE

Do **NOT** share these (they are environment-specific):

- `.venv/` - Virtual environment (will be recreated on target machine)
- `__pycache__/` - Python cache files
- `.git/` - Git history (unless you want version control)
- `*.pyc` - Compiled Python files
- Any markdown files with session notes (CLAUDE.md, SESSION_*.md, etc.)

## Distribution Methods

### Method 1: Git Repository (Recommended)

If you're using Git:

```bash
# On the source machine, commit your changes
git add .
git commit -m "Ready for distribution"
git push

# On the target machine
git clone <repository-url>
cd webpage_projector
./install.sh
./run.sh
```

**Advantages:**
- Easy updates via `git pull`
- Version control
- Smallest transfer size

### Method 2: ZIP File Distribution

For sharing without Git:

1. **Create the distribution package:**

```bash
# On the source machine
cd /path/to/webpage_projector

# Create a zip excluding unnecessary files
zip -r webpage_projector.zip . \
  -x "*.git*" \
  -x "*__pycache__*" \
  -x "*.pyc" \
  -x ".venv/*" \
  -x "*.md" \
  -x "old-version/*" \
  -x "tests/*" \
  -x ".python-version" \
  -x "*.sh~" \
  -x "CLAUDE.md" \
  -x "*SESSION*.md" \
  -x "*PHASE*.md"
```

2. **On the target machine:**

```bash
# Extract the archive
unzip webpage_projector.zip -d webpage_projector
cd webpage_projector

# Run installation
./install.sh

# Run the application
./run.sh
```

### Method 3: Cloud Storage (Dropbox, Google Drive, etc.)

1. Upload the entire project folder (excluding `.venv` and `.git`)
2. Share the link with the target user
3. They download and extract
4. Run `./install.sh` and then `./run.sh`

## Installation on Target Machine

### Prerequisites

The target Mac needs:
- **macOS** (tested on macOS 10.15+)
- **Python 3.12 or higher** - [Download here](https://www.python.org/downloads/)
- **Internet connection** (for downloading dependencies)

### Step-by-Step for End User

1. **Download/Clone the project**
   ```bash
   cd ~/Downloads/webpage_projector
   ```

2. **Make scripts executable** (if needed)
   ```bash
   chmod +x install.sh run.sh
   ```

3. **Run installation**
   ```bash
   ./install.sh
   ```

   This will:
   - Check Python version
   - Install `uv` package manager
   - Create virtual environment
   - Install all dependencies
   - Create default `config.json`

4. **Run the application**
   ```bash
   ./run.sh
   ```

### First-Time Configuration

After first run, users should configure:

1. **config.json** - Edit to set:
   - Google Slides ID for agenda
   - Google Meet URL (if using)
   - Font sizes (if needed)

2. **Dual Monitor Setup**
   - Connect second monitor
   - The app auto-detects displays

3. **Google Meet Automation** (Optional, macOS only):
   - Grant Accessibility permissions when prompted
   - Enable Chrome: View > Developer > Allow JavaScript from Apple Events

## Troubleshooting on Target Machine

### Python Version Issues

```bash
# Check Python version
python3 --version

# Should be 3.12 or higher
# If not, download from https://www.python.org/downloads/
```

### Permission Issues

```bash
# Make scripts executable
chmod +x install.sh run.sh
```

### Missing Dependencies

```bash
# Reinstall dependencies
source .venv/bin/activate
uv pip install -e .
```

### wxPython Installation Fails

On some Macs, wxPython may need system dependencies:

```bash
# If installation fails, try:
brew install wxpython
```

## Updating the Application

### If using Git:

```bash
cd webpage_projector
git pull
source .venv/bin/activate
uv pip install -e .  # Update dependencies if changed
./run.sh
```

### If using ZIP files:

1. Download new version
2. **Backup your config.json**
3. Extract new version
4. **Restore your config.json**
5. Run `./install.sh` again
6. Run `./run.sh`

## Creating a Portable Package

For the most user-friendly distribution, you can create a single-command installer:

```bash
# Create an installer script
cat > easy_install.sh << 'EOF'
#!/bin/bash
echo "Webpage Projector - Quick Installer"
echo "===================================="
echo ""
echo "This will download and install Webpage Projector"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Download from your repository
    git clone <your-repo-url> webpage_projector
    cd webpage_projector
    ./install.sh
    echo ""
    echo "Installation complete! Run with: ./run.sh"
fi
EOF

chmod +x easy_install.sh
```

Then users only need to run:
```bash
curl -sSL <url-to-easy_install.sh> | bash
```

## Security Notes

- **Never share `.env` files** if you add them later
- **Remove sensitive data** from `config.json` before sharing
- **Review** `config.json` for any personal meeting URLs or IDs

## Minimum File Set

The absolute minimum files needed for distribution:

```
webpage_projector/
├── src/                    # All application code
├── books/                  # Bible text files
├── books.csv              # Bible metadata
├── hymns.csv              # Hymn data
├── ncf_background.png     # Background image
├── pyproject.toml         # Dependencies
├── uv.lock                # Locked versions
├── install.sh             # Installer
├── run.sh                 # Run script
└── README.md              # Documentation
```

Total size: ~2-5 MB (depending on how many Bible versions are included)

## Support

For issues on the target machine:

1. Check Python version: `python3 --version` (must be 3.12+)
2. Try reinstalling: `./install.sh`
3. Check logs in the terminal output
4. Ensure macOS is up to date
5. Verify internet connection (needed for initial install)