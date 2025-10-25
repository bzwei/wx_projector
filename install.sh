#!/bin/bash
# Webpage Projector - One-Step Installation Script for macOS
# This script will install all dependencies and set up the application

set -e  # Exit on error

echo "======================================"
echo "Webpage Projector - Installation"
echo "======================================"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script is designed for macOS only."
    exit 1
fi

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.12 or higher from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
REQUIRED_VERSION="3.12"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
    echo "Error: Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    echo "Please install Python 3.12+ from https://www.python.org/downloads/"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION detected"
echo ""

# Check/Install uv
echo "Checking for uv package manager..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add uv to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        echo "Error: uv installation failed."
        echo "Please install manually: https://github.com/astral-sh/uv"
        exit 1
    fi
fi
echo "✓ uv package manager is ready"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists, skipping creation."
else
    uv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .
echo "✓ Dependencies installed"
echo ""

# Check for required data files
echo "Checking data files..."
if [ ! -d "books" ]; then
    echo "Warning: 'books' directory not found. Bible verses may not work."
fi

if [ ! -f "hymns.csv" ]; then
    echo "Warning: 'hymns.csv' not found. Hymn projection may not work."
fi

if [ ! -f "config.json" ]; then
    echo "Creating default config.json..."
    cat > config.json << 'EOF'
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
    "slides_id": ""
  },
  "history": {
    "max_history_size": 30
  },
  "google_meet": {
    "meeting_url": ""
  }
}
EOF
    echo "✓ Created default config.json"
fi
echo ""

echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "To run the application:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  source .venv/bin/activate"
echo "  python src/main.py"
echo ""
echo "For Google Meet automation features:"
echo "  1. Grant Accessibility permissions when prompted"
echo "  2. Enable Chrome > View > Developer > Allow JavaScript from Apple Events"
echo ""