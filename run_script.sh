#!/bin/bash

# Script to run Python programs with the virtual environment
# Usage: ./run_script.sh <script_name.py> [arguments...]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found. Creating it now..."
    python3 -m venv "$VENV_PATH"
    echo "✅ Virtual environment created."
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Check if requirements are installed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installing requirements..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
    echo "✅ Requirements installed."
fi

# Check if script name is provided
if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <script_name.py> [arguments...]"
    echo ""
    echo "Available scripts:"
    for script in "$SCRIPT_DIR"/*.py; do
        if [ -f "$script" ]; then
            echo "  - $(basename "$script")"
        fi
    done
    exit 1
fi

SCRIPT_NAME="$1"
shift  # Remove script name from arguments

# Check if script exists
if [ ! -f "$SCRIPT_DIR/$SCRIPT_NAME" ]; then
    echo "❌ Script '$SCRIPT_NAME' not found in $SCRIPT_DIR"
    exit 1
fi

echo "🚀 Running $SCRIPT_NAME with virtual environment..."
echo "─────────────────────────────────────────────"

# Run the script with remaining arguments
python3 "$SCRIPT_DIR/$SCRIPT_NAME" "$@"