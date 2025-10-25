# Release Checklist for Webpage Projector

Use this checklist before distributing the application to ensure a clean package.

## Pre-Release Steps

### 1. Code and Dependencies

- [ ] All features working and tested
- [ ] Dependencies in `pyproject.toml` are accurate
- [ ] `uv.lock` is up to date: `uv lock`
- [ ] No hardcoded paths or local-specific configurations

### 2. Clean Up Development Files

```bash
# Remove development artifacts
rm -rf __pycache__/
rm -rf .venv/
rm -rf *.egg-info/
rm -rf build/
rm -rf dist/

# Remove test outputs
rm -f *.log
rm -f *.tmp

# Check what files will be committed
git status
```

### 3. Configuration

- [ ] Review `config.json` for any sensitive data
- [ ] Remove or anonymize:
  - [ ] Google Meet URLs
  - [ ] Google Slides IDs (or use example IDs)
  - [ ] Any personal information

**Option 1:** Delete `config.json` (will be auto-generated)
```bash
rm config.json
```

**Option 2:** Create template
```json
{
  "window": {
    "control_panel": {
      "width": 1000,
      "height": 700
    }
  },
  "display": {
    "preferred_display_index": 1,
    "auto_detect": true
  },
  "bible": {
    "default_versions": ["cuv"],
    "font_size_chinese": 80,
    "font_size_english": 76
  },
  "agenda": {
    "slides_id": "YOUR_GOOGLE_SLIDES_ID_HERE"
  },
  "history": {
    "max_history_size": 30
  },
  "google_meet": {
    "meeting_url": "https://meet.google.com/YOUR-MEETING-CODE"
  }
}
```

### 4. Documentation

- [ ] README.md is up to date
- [ ] DISTRIBUTION.md is accurate
- [ ] All example commands have been tested
- [ ] Screenshots are current (if any)

### 5. Scripts

- [ ] `install.sh` works on a clean machine
- [ ] `run.sh` works after installation
- [ ] Scripts have execute permissions:
  ```bash
  chmod +x install.sh run.sh
  ```

### 6. Verify .gitignore

- [ ] `.gitignore` excludes development files
- [ ] Check with: `git status --ignored`
- [ ] No `.venv/` or `__pycache__/` in repo

### 7. Essential Files Included

Verify these files/folders exist:

```bash
# Required files
ls -la src/          # Source code
ls -la books/        # Bible text files
ls -la books.csv     # Bible metadata
ls -la hymns.csv     # Hymn data
ls -la ncf_background.png  # Background image
ls -la pyproject.toml      # Dependencies
ls -la uv.lock            # Locked dependencies
ls -la install.sh         # Installer
ls -la run.sh             # Run script
ls -la README.md          # Documentation
```

## Distribution Methods

### Method 1: Git Repository (Recommended)

```bash
# 1. Commit all changes
git add .
git commit -m "Release version X.X.X"
git tag -a vX.X.X -m "Release version X.X.X"

# 2. Push to remote
git push origin main
git push origin --tags

# 3. Create GitHub release (optional)
# Go to GitHub -> Releases -> Draft a new release
```

### Method 2: ZIP Archive

```bash
# Create clean distribution archive
cd ..
zip -r webpage_projector-vX.X.X.zip webpage_projector \
  -x "webpage_projector/.git/*" \
  -x "webpage_projector/.venv/*" \
  -x "webpage_projector/__pycache__/*" \
  -x "webpage_projector/*.pyc" \
  -x "webpage_projector/.DS_Store" \
  -x "webpage_projector/old-version/*" \
  -x "webpage_projector/tests/*" \
  -x "webpage_projector/CLAUDE.md" \
  -x "webpage_projector/*SESSION*.md" \
  -x "webpage_projector/PHASE*.md" \
  -x "webpage_projector/test_*.sh" \
  -x "webpage_projector/test_*.py" \
  -x "webpage_projector/DEBUG_RUN.sh"

# Verify archive contents
unzip -l webpage_projector-vX.X.X.zip
```

## Post-Distribution Testing

Test on a clean Mac (or fresh user account):

```bash
# 1. Extract/clone the distribution
cd webpage_projector

# 2. Verify files
ls -la

# 3. Run installation
./install.sh

# 4. Check installation output
# Should see: ✓ Python version detected
# Should see: ✓ uv package manager is ready
# Should see: ✓ Virtual environment created
# Should see: ✓ Dependencies installed
# Should see: Installation Complete!

# 5. Run the application
./run.sh

# 6. Test basic functionality
# - Control panel opens
# - Can search for Bible verses
# - Can project to secondary display (if available)
# - Settings can be adjusted
```

## Version Numbering

Update version in:
- [ ] `pyproject.toml` - `version = "X.X.X"`
- [ ] `README.md` - Add to changelog if exists
- [ ] Git tag: `git tag -a vX.X.X`

Semantic versioning:
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

## Common Issues to Check

### Installation Issues
- [ ] Python version check works
- [ ] uv installation succeeds
- [ ] Dependencies install without errors
- [ ] Virtual environment created successfully

### Runtime Issues
- [ ] Application starts without errors
- [ ] Books directory loads correctly
- [ ] Hymns data loads correctly
- [ ] Background image displays
- [ ] Config file created if missing

### macOS Specific
- [ ] AppleScript features don't crash on other systems
- [ ] Accessibility permission prompts work correctly
- [ ] Chrome automation gracefully degrades if Chrome not installed

## Final Checklist

Before sharing:

- [ ] All tests pass (if you have tests)
- [ ] Application runs on clean machine
- [ ] Documentation is clear and accurate
- [ ] No sensitive data in config files
- [ ] Install script works
- [ ] Run script works
- [ ] .gitignore is complete
- [ ] Version number updated
- [ ] Git tag created (if using Git)

## Distribution Package Contents

Final package should contain:

```
webpage_projector/
├── src/                    # Application source code
├── books/                  # Bible text files
├── books.csv              # Bible metadata
├── hymns.csv              # Hymn database
├── ncf_background.png     # Background image
├── pyproject.toml         # Project config & dependencies
├── uv.lock                # Locked dependency versions
├── install.sh             # Installation script
├── run.sh                 # Run script
├── README.md              # User documentation
├── DISTRIBUTION.md        # Distribution guide
└── .gitignore            # Git exclusions
```

**Approximate size:** 2-5 MB

## Post-Release

- [ ] Send installation instructions to users
- [ ] Provide support contact information
- [ ] Monitor for installation issues
- [ ] Create quick troubleshooting guide if needed

## Notes

- Always test on a clean machine before distributing
- Keep sensitive config data out of the repository
- Update documentation with each release
- Tag releases for easy version tracking