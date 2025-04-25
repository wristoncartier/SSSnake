#!/bin/bash

# Create build directory
mkdir -p build
cd build

# Run CMake
cmake ..

# Build the project
make

# Create lib directory in project root if it doesn't exist
mkdir -p ../lib

# Copy the dylib to the lib directory
cp lib/roblox_injector.dylib ../lib/
