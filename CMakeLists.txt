cmake_minimum_required(VERSION 3.10)
project(script_executor)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Enable exceptions
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fexceptions")

# Set output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Add source files
set(SOURCES
    src/injector.cpp
    src/roblox_api.cpp
    src/memory.cpp
)

# Create shared library
add_library(roblox_injector SHARED ${SOURCES})

# Set include directories
target_include_directories(roblox_injector PRIVATE src)

# Set compile options
target_compile_options(roblox_injector PRIVATE -Wall -Wextra)

# Set library properties
set_target_properties(roblox_injector PROPERTIES
    PREFIX ""
    SUFFIX ".dylib"
)

# Link system libraries
target_link_libraries(roblox_injector PRIVATE
    "-framework Foundation"
    "-framework CoreFoundation"
    "-framework CoreServices"
)
