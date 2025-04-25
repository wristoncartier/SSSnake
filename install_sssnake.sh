#!/bin/bash

# SSSnake Installer Script
echo "Installing SSSnake to Applications folder..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install dependencies
echo "Installing required Python packages..."
python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"

# Check if the application bundle exists
if [ ! -d "$SCRIPT_DIR/SSSnake.app" ]; then
    echo "Error: SSSnake.app not found in the current directory!"
    exit 1
fi

# Copy the application to Applications folder
echo "Copying SSSnake.app to Applications folder..."
cp -R "$SCRIPT_DIR/SSSnake.app" /Applications/

# Set executable permissions
chmod +x /Applications/SSSnake.app/Contents/MacOS/SSSnake

# Create lib directory if it doesn't exist
mkdir -p /Applications/SSSnake.app/Contents/Resources/lib

# Copy all Python files and resources
echo "Copying application files..."
cp "$SCRIPT_DIR"/*.py /Applications/SSSnake.app/Contents/Resources/
cp -R "$SCRIPT_DIR/icons" /Applications/SSSnake.app/Contents/Resources/

# Create lib directory in the app's Resources
mkdir -p /Applications/SSSnake.app/Contents/Resources/lib

# Copy the DLL if it exists
if [ -d "$SCRIPT_DIR/lib" ]; then
    cp -R "$SCRIPT_DIR/lib"/* /Applications/SSSnake.app/Contents/Resources/lib/
fi

# Update the launcher script to use the bundled resources
cat > /Applications/SSSnake.app/Contents/MacOS/SSSnake << 'EOL'
#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Go up to the Contents directory
CONTENTS_DIR="$( dirname "$DIR" )"
# Resources directory
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Make sure we have the right Python
PYTHON="/usr/bin/env python3"

# Change to the resources directory
cd "$RESOURCES_DIR"

# Run the application
$PYTHON "$RESOURCES_DIR/main.py"
EOL

# Make the launcher executable
chmod +x /Applications/SSSnake.app/Contents/MacOS/SSSnake

echo "Installation complete! SSSnake has been installed to your Applications folder."
echo "You can now run SSSnake from your Applications folder or Launchpad."
