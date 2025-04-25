#!/bin/bash

# SSSnake Setup Script - WRISTONCARTIER Edition
echo "Welcome to SSSnake - WRISTONCARTIER Edition Setup"
echo "-----------------------------------------------"

# 1. Create project directory
echo "Creating project directory..."
mkdir -p SSSnake_WristonCartier
cd SSSnake_WristonCartier

# 2. Download required files
echo "Downloading required files..."
curl -s https://raw.githubusercontent.com/wristoncartier/SSSnake/main/main.py -o main.py
curl -s https://raw.githubusercontent.com/wristoncartier/SSSnake/main/run_sssnake.command -o run_sssnake.command
curl -s https://raw.githubusercontent.com/wristoncartier/SSSnake/main/requirements.txt -o requirements.txt

# 3. Make launcher executable
chmod +x run_sssnake.command

# 4. Install dependencies
echo "Installing required dependencies..."
pip3 install -r requirements.txt

echo "Setup complete!"
echo "You can now run SSSnake with ./run_sssnake.command"
