#!/bin/bash
# Webpage Projector - Quick Run Script
# Run this after installation to start the application

set -e

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./install.sh first"
    exit 1
fi

# Activate virtual environment and run
source .venv/bin/activate
python src/main.py