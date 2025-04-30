# Installation Guide

This guide provides instructions for installing Pockage on different operating systems.

## Prerequisites

- Python 3.7 or higher
- Git (optional, for development)
- C/C++ compiler (varies by platform)

## Installation Methods

### Quick Installation

#### macOS/Linux
```bash
curl -L https://raw.githubusercontent.com/Jaseunda/pockage/main/install.sh | bash
```

#### Windows
```powershell
curl -L https://raw.githubusercontent.com/Jaseunda/pockage/main/install.bat -o install.bat && install.bat
```

### Manual Installation

If you prefer to install manually or the quick installation doesn't work for you:

1. Clone the repository:
   ```bash
   git clone https://github.com/Jaseunda/pockage.git
   cd pockage
   ```

2. Install using pip:
   ```bash
   pip install -e .
   ```

## Platform-Specific Requirements

### macOS

- Xcode Command Line Tools: `xcode-select --install`
- Homebrew (recommended): `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

### Windows

- Visual Studio with C++ development tools or MinGW
- Windows SDK (for some libraries)

### Linux

- GCC/G++ and build essentials:
  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install build-essential
  
  # Fedora
  sudo dnf install gcc-c++ make
  
  # Arch Linux
  sudo pacman -S base-devel
  ```

## Verifying Installation

To verify that Pockage was installed correctly, run:

```bash
pockage version
```

You should see the current version of Pockage displayed.

## Troubleshooting

### Common Issues

1. **Command not found**: Ensure that Python's bin directory is in your PATH
2. **Permission denied**: Try running the installation with elevated privileges
3. **Missing dependencies**: Install required Python packages manually with `pip install requests tqdm colorama`

### Getting Help

If you encounter any issues during installation, please [open an issue](https://github.com/Jaseunda/pockage/issues) on GitHub with details about your system and the error messages you're seeing.

## Next Steps

Now that you have Pockage installed, check out the [Quick Start Guide](QUICKSTART.md) to create your first project.