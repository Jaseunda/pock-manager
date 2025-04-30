# Quick Start Guide

This guide will help you get started with Pockage, from creating your first project to building and running it.

## Creating a New Project

```bash
# Create and enter project directory
mkdir myproject
cd myproject

# Initialize project (like npm init)
pockage new
```

This will create a basic project structure with a `pockage.json` file and some starter code.

### Project with Specific Platforms

You can specify which platforms you want to target when creating a new project:

```bash
pockage new -p macos windows linux
```

This will enable build configurations for macOS, Windows, and Linux in your `pockage.json` file.

## Project Structure

After initializing a project, you'll have a structure similar to this:

```
myproject/
├── pockage.json     # Project configuration
├── src/
│   └── main.cpp     # Main source file
└── include/         # Header files
```

## Managing Dependencies

### Installing Dependencies

To install all dependencies defined in your `pockage.json` file:

```bash
pockage install
```

This will download and set up all required libraries in the `libs/` directory.

### Adding a Specific Library

To add a specific library:

```bash
pockage install sdl2
```

Or edit your `pockage.json` file manually and add it to the dependencies section:

```json
{
  "dependencies": {
    "sdl2": "2.28.5",
    "imgui": "1.89.9"
  }
}
```

Then run `pockage install` to install the new dependencies.

## Building Your Project

To build your project:

```bash
pockage build
```

This will compile your code and create an executable in the `build/` directory.

### Platform-Specific Builds

To build for a specific platform:

```bash
pockage build --platform macos
```

## Running Your Project

To run your project after building:

```bash
pockage run
```

This will execute the built application.

## Creating a GUI Application

Pockage includes templates for different types of applications. To create a GUI application with SDL2 and ImGui:

```bash
pockage new --template gui
```

This will set up a project with SDL2 and ImGui dependencies and boilerplate code for a GUI application.

## Checking Project Status

To see information about your Pockage installation and project:

```bash
pockage status
```

This will show version information, storage usage, and other details.

## Scanning for Projects

To scan your system for Pockage projects:

```bash
pockage scan
```

This will search for `pockage.json` files and list all found projects.

## Next Steps

- Check out the [Supported Libraries](LIBRARIES.md) to see what libraries you can use in your projects
- Learn about [Advanced Features](ADVANCED.md) for more complex project configurations
- Explore [Platform Support](PLATFORMS.md) for platform-specific details