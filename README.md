<p align="center">
  <img src="assets/banner.png" alt="Pockage Banner" width="100%">
</p>

# 🚢📦 Pockage — The npm for C/C++

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-early%20development-orange)](https://github.com/Jaseunda/pockage)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/Jaseunda/pockage)

> ⚠️ **Early Development**: Pockage is in its early stages. Expect breaking changes and limited features.
>
> 🧪 **Project Status**: Core functionality works, but templated applications might have issues. Projects created from scratch work fine.

Pockage is a modern package manager for C/C++ projects, inspired by npm and cargo. Whether you're building games, applications, system software, or operating systems, Pockage makes dependency management simple and efficient.

## 📚 Documentation

Detailed documentation is available in the [docs](docs/) directory:

- [Installation Guide](docs/INSTALLATION.md) - How to install Pockage on different platforms
- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running with your first project
- [Supported Libraries](docs/LIBRARIES.md) - List of libraries and how to add new ones
- [Advanced Features](docs/ADVANCED.md) - Platform-specific configurations and advanced usage
- [Project History](docs/HISTORY.md) - Origins and evolution of Pockage
- [License and Warranty](docs/LICENSE.md) - License information and warranty disclaimer

## 🚀 Quick Installation

### macOS/Linux
```bash
curl -L https://raw.githubusercontent.com/Jaseunda/pockage/main/install.sh | bash
```

### Windows
```powershell
curl -L https://raw.githubusercontent.com/Jaseunda/pockage/main/install.bat -o install.bat && install.bat
```

## 📋 Command Reference

> **Tip**: You can use `poc` as a shorter alias for `pockage` in all commands.

```bash
# Create a new project
pockage new [--template <template>] [-p <platforms>]
# or: poc new [--template <template>] [-p <platforms>]

# Install dependencies
pockage install [library]
# or: poc install [library]

# Build project
pockage build [--platform <platform>]
# or: poc build [--platform <platform>]

# Run project
pockage run
# or: poc run

# Show package status
pockage status
# or: poc status

# Scan for projects
pockage scan [--scan-dir <directory>] [--scan-depth <depth>]
# or: poc scan [--scan-dir <directory>] [--scan-depth <depth>]

# Update libraries
pockage update
# or: poc update

# Uninstall a library
pockage uninstall <library>
# or: poc uninstall <library>

# Search for libraries
pockage search <query>
# or: poc search <query>

# Show version
pockage version
# or: poc version
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📢 Support

For support, please open an issue in the [GitHub repository](https://github.com/Jaseunda/pockage).

## 🙏 Acknowledgments

- [npm](https://www.npmjs.com/) for inspiration
- [SDL2](https://www.libsdl.org/) for cross-platform development
- [Dear ImGui](https://github.com/ocornut/imgui) for the GUI system
- All other library authors and maintainers
- [PockOS Project](https://github.com/PockStudio/pockos) - The project that inspired Pockage
