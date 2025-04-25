#!/bin/bash

# SSSnake Launcher Script - WRISTONCARTIER Edition
echo "Starting SSSnake - WRISTONCARTIER Edition..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Make sure we have the right Python
PYTHON="/usr/bin/env python3"

# Function to check if a Python package is installed
check_package() {
    $PYTHON -c "import $1" 2>/dev/null
    return $?
}

# Function to install a package if it's not already installed
ensure_package() {
    if ! check_package "$1"; then
        echo "Installing required package: $1"
        $PYTHON -m pip install "$1" --user
    fi
}

# Ensure required packages are installed
echo "Checking dependencies..."
ensure_package "PyQt6"
ensure_package "psutil"
ensure_package "requests"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the application
echo "Launching SSSnake - WRISTONCARTIER Edition..."
$PYTHON "$SCRIPT_DIR/main.py"
