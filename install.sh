#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[Pockage]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.7 or higher."
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    if (( $(echo "$PYTHON_VERSION < 3.7" | bc -l) )); then
        print_error "Python version must be 3.7 or higher. Current version: $PYTHON_VERSION"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        print_warning "pip is not installed. Installing pip..."
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    fi
}

# Install Pockage
install_pockage() {
    print_message "Installing Pockage..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Download Pockage
    print_message "Downloading Pockage..."
    curl -L https://github.com/yourusername/pockage/archive/refs/heads/main.zip -o pockage.zip
    
    # Extract and install
    print_message "Installing..."
    unzip pockage.zip
    cd pockage-main
    
    # Install dependencies and Pockage
    $PYTHON_CMD -m pip install -e .
    
    # Clean up
    cd ..
    rm -rf "$TEMP_DIR"
    
    print_message "Pockage installed successfully!"
}

# Main installation process
main() {
    print_message "Starting Pockage installation..."
    
    # Check system requirements
    check_python
    check_pip
    
    # Install Pockage
    install_pockage
    
    # Add to PATH if needed
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! grep -q "export PATH=\"\$HOME/Library/Python/3.9/bin:\$PATH\"" ~/.zshrc; then
            echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc
            print_message "Added Pockage to PATH in ~/.zshrc"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.bashrc; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            print_message "Added Pockage to PATH in ~/.bashrc"
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        print_warning "Please add %APPDATA%\\Python\\Python39\\Scripts to your PATH manually"
    fi
    
    print_message "Installation complete! Please restart your terminal or run 'source ~/.zshrc' (macOS/Linux) to use Pockage."
}

# Run the installation
main 