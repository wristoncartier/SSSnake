# Use clang++ on macOS
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    CXX = clang++
    CXXFLAGS = -std=c++17 -Wall -Wextra -fPIC -O2 -I/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include -I/Library/Developer/CommandLineTools/usr/include/c++/v1
    LDFLAGS = -shared -undefined dynamic_lookup
else
    CXX = g++
    CXXFLAGS = -std=c++17 -Wall -Wextra -fPIC -O2
    LDFLAGS = -shared -pthread
endif

# Target platform detection
ifeq ($(UNAME_S),Darwin)
    TARGET = roblox_injector.dylib
    LDFLAGS += -framework Foundation -framework AppKit
else ifeq ($(UNAME_S),Linux)
    TARGET = roblox_injector.so
else
    TARGET = roblox_injector.dll
    LDFLAGS = -shared -static-libgcc -static-libstdc++
endif

# Source files
SRCS = roblox_injector.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Build rule for the target
all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) $(OBJS) -o $@ $(LDFLAGS)

# Build rule for object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean rule
clean:
	rm -f $(OBJS) $(TARGET)

# Install rule
install:
	mkdir -p ../lib
	cp $(TARGET) ../lib/

.PHONY: all clean install
