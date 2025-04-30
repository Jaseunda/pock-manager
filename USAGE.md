# Pockage Usage Guide

## Overview

Pockage is "The npm for C/C++" - a powerful dependency manager and build system for C/C++ projects. This guide covers all available commands and features to help you get the most out of Pockage.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Install from Source

```bash
# Install setuptools if not already installed
pip3 install setuptools

# Install Pockage
pip3 install .

# Or install in development mode
pip3 install -e .
```

### Using Virtual Environment (Recommended)

```bash
# Create a virtual environment
python3 -m venv pockage-env

# Activate the virtual environment
source pockage-env/bin/activate  # On Unix/macOS
pockage-env\Scripts\activate    # On Windows

# Install Pockage
pip install .
```

## Commands

### Version

Check the installed version of Pockage:

```bash
pockage version
```

### Creating Projects

#### Basic Project Creation

Create a new project in the current directory:

```bash
pockage new
```

#### Using Templates

Pockage supports different project templates:

```bash
# Create a basic Hello World project (default)
pockage new hello-world

# Create a GUI project with ImGui and SDL2
pockage new gui
# OR using the new@format syntax
pockage new@gui

# Create an SDL2 project
pockage new sdl2
```

#### Specifying Platforms

Create a project for specific platforms:

```bash
# Create a project for macOS, iOS, and Linux
pockage new -p macos ios linux

# Create a GUI project for Windows and macOS
pockage new gui -p windows macos
# OR using the new@format syntax
pockage new@gui -p windows macos
```

#### Creating in a New Directory

Create a project in a new directory:

```bash
pockage make my_project

# With specific platforms
pockage make my_project -p macos windows

# With a specific template
pockage make my_project hello-world
pockage make my_project gui
```

### Building Projects

Build the current project:

```bash
pockage build
```

Build for a specific platform:

```bash
pockage build macos
pockage build windows
pockage build linux
pockage build ios
pockage build android
```

### Running Projects

Run the built project:

```bash
pockage run
pockage run macos
pockage run windows
pockage run linux
pockage run ios
pockage run android
```

### Managing Dependencies

#### Installing Dependencies

Install all dependencies defined in pockage.json:

```bash
pockage install
```

Install a specific library:

```bash
pockage install sdl2
```

#### Uninstalling Dependencies

Remove a dependency:

```bash
pockage uninstall sdl2
```

### Project Information

Display information about the current project:

```bash
pockage info
```

### Searching for Libraries

Search for available libraries:

```bash
pockage search sdl
```

### System Check

Check your system setup for compatibility:

```bash
pockage doctor
```

### Configuration

Set project-specific configuration:

```bash
pockage config-set build.compiler clang++
```

Set global configuration:

```bash
pockage config-set cache_dir /path/to/cache
```

## Project Templates

Pockage offers several project templates to get you started quickly:

### Hello World (Default)

A minimal C++ project that prints "Hello, World!" to the console.

```bash
pockage new
# or
pockage new hello-world
```

### GUI

A graphical user interface project using Dear ImGui and SDL2, featuring:
- A resizable window
- Text display
- Interactive controls (button, color picker)
- Customizable background color

```bash
pockage new gui
# or using the new@format syntax
pockage new@gui
```

### SDL2

A basic SDL2 project with a window and renderer.

```bash
pockage new sdl2
```

## Platform-Specific Build Configurations

Pockage supports building for multiple platforms with platform-specific settings:

- **macOS**: Uses clang++ with frameworks support
- **Windows**: Uses g++ with Windows-specific settings
- **Linux**: Uses g++ with Linux-specific settings
- **iOS**: Uses clang++ with iOS SDK and arm64 architecture
- **Android**: Uses clang++ with shared library output

Enable platforms during project creation:

```bash
pockage new -p macos windows linux
```

Or manually edit the `pockage.json` file to enable or disable platforms.

## Advanced Features

### Application Icons

Pockage automatically includes a complete set of application icons for macOS and iOS projects. The icons are stored in the `resources/AppIcon.appiconset` directory and are used when building app bundles. You can replace these icons with your own if desired.

### IDE Integration

Pockage can open your project in various IDEs:

```bash
# Open project in Xcode
pockage open xcode

# Open project specifically for iOS development
pockage open ios

# Open project specifically for macOS development
pockage open macos

# Open project in Android Studio
pockage open android
```

### Parallel Building

Pockage automatically builds projects using multiple cores for faster compilation.

### Version Locking

Dependencies are locked to specific versions in the pockage.json file to ensure reproducible builds.

### Efficient Package Caching

Downloaded packages are cached to avoid redundant downloads and speed up future builds.

### macOS App Bundles

When building for macOS, Pockage creates proper `.app` bundles with the correct structure:

```
YourApp.app/
  Contents/
    MacOS/
      YourApp (executable)
    Frameworks/
      SDL2.framework/
    Resources/
      (app icons)
    Info.plist
```

This allows your applications to be distributed and run like standard macOS applications.

## Project Structure

A typical Pockage project has the following structure:

```
project/
├── pockage.json       # Project configuration
├── src/               # Source code
│   └── main.cpp       # Main source file
├── include/           # Header files
├── libs/              # Dependencies
└── build/             # Build output
    ├── macos/         # macOS build
    ├── windows/       # Windows build
    └── linux/         # Linux build
```

## Configuration File (pockage.json)

The `pockage.json` file defines your project's configuration:

```json
{
  "name": "my_project",
  "version": "0.1.0",
  "description": "A new project built with Pockage!",
  "dependencies": {
    "sdl2": "2.28.5",
    "imgui": "1.89.9"
  },
  "platforms": {
    "macos": {
      "enabled": true,
      "build": {
        "compiler": "clang++",
        "cpp_version": "c++17",
        "output": "build/macos/my_project",
        "include_paths": ["include", "libs/sdl2/SDL2.framework/Headers"],
        "framework_paths": ["libs/sdl2"],
        "frameworks": ["SDL2"],
        "build_flags": "-Wall -Wextra"
      }
    },
    "windows": {
      "enabled": true,
      "build": {
        "compiler": "g++",
        "cpp_version": "c++17",
        "output": "build/windows/my_project.exe",
        "include_paths": ["include", "libs/sdl2/include"],
        "lib_paths": ["libs/sdl2/lib"],
        "link_libraries": ["SDL2"],
        "build_flags": "-Wall -Wextra"
      }
    }
  },
  "run": {
    "executable": "build/macos/my_project"
  }
}
```

## Troubleshooting

### Common Issues

#### Missing setuptools

If you encounter a `ModuleNotFoundError` for `pkg_resources` or `setuptools`, install setuptools:

```bash
pip3 install setuptools
```

#### Externally-managed-environment Error

If you see an "externally-managed-environment" error when installing with pip, use one of these solutions:

1. Use a virtual environment (recommended):
   ```bash
   python3 -m venv pockage-env
   source pockage-env/bin/activate
   pip install .
   ```

2. Use the `--user` flag:
   ```bash
   pip3 install --user .
   ```

3. Use the `--break-system-packages` flag (not recommended for production):
   ```bash
   pip3 install --break-system-packages .
   ```

#### Command Not Found

If the `pockage` command is not found after installation, ensure:

1. The package was installed correctly
2. The virtual environment is activated (if using one)
3. The installation directory is in your PATH

## Contributing

Contributions to Pockage are welcome! See the CONTRIBUTING.md file for details.

## License

Pockage is licensed under the MIT License. See the LICENSE file for details.