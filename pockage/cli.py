#!/usr/bin/env python3

import argparse
import json
import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
import tarfile
import platform
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging
import hashlib
import tempfile
import re
import glob
import pkg_resources
import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pockage')

class PockageManager:
    def __init__(self):
        self.config = self._load_config()
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.lib_registry = self._load_lib_registry()
        self.global_config = self._load_global_config()

    def _load_config(self) -> Dict:
        config_path = Path("pockage.json")
        if not config_path.exists():
            return {}
        
        with open(config_path) as f:
            return json.load(f)

    def _load_global_config(self) -> Dict:
        config_path = Path.home() / ".pockage" / "config.json"
        if not config_path.exists():
            return {}
        
        with open(config_path) as f:
            return json.load(f)

    def _save_global_config(self):
        config_path = Path.home() / ".pockage"
        config_path.mkdir(parents=True, exist_ok=True)
        
        with open(config_path / "config.json", "w") as f:
            json.dump(self.global_config, f, indent=2)

    def _load_lib_registry(self) -> Dict:
        """Load library registry with official download URLs and build instructions."""
        return {
            "sdl2": {
                "urls": {
                    "darwin": "https://github.com/libsdl-org/SDL/releases/download/release-{version}/SDL2-{version}.dmg",
                    "windows": "https://github.com/libsdl-org/SDL/releases/download/release-{version}/SDL2-devel-{version}-VC.zip",
                    "linux": "https://github.com/libsdl-org/SDL/releases/download/release-{version}/SDL2-{version}.tar.gz"
                },
                "extract": {
                    "darwin": self._extract_dmg,
                    "windows": self._extract_zip,
                    "linux": self._extract_tar
                }
            },
            "imgui": {
                "urls": {
                    "all": "https://github.com/ocornut/imgui/archive/refs/tags/v{version}.zip"
                },
                "extract": {
                    "all": self._extract_zip
                }
            }
        }

    def _extract_dmg(self, file_path: str, extract_path: str):
        """Extract a DMG file on macOS."""
        try:
            # Mount the DMG
            mount_point = tempfile.mkdtemp()
            subprocess.run(["hdiutil", "attach", file_path, "-mountpoint", mount_point], check=True)
            
            # Copy contents
            shutil.copytree(mount_point, extract_path, dirs_exist_ok=True)
            
            # Unmount
            subprocess.run(["hdiutil", "detach", mount_point], check=True)
            shutil.rmtree(mount_point)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract DMG: {e}")
            sys.exit(1)

    def _extract_zip(self, file_path: str, extract_path: str):
        """Extract a ZIP file."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        except zipfile.BadZipFile as e:
            logger.error(f"Failed to extract ZIP: {e}")
            sys.exit(1)

    def _extract_tar(self, file_path: str, extract_path: str):
        """Extract a TAR file."""
        try:
            with tarfile.open(file_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_path)
        except tarfile.TarError as e:
            logger.error(f"Failed to extract TAR: {e}")
            sys.exit(1)

    def _install_library(self, library: str):
        """Install a specific library."""
        if library not in self.lib_registry:
            logger.error(f"Library {library} not found in registry")
            sys.exit(1)

        version = self.config["dependencies"][library]
        lib_info = self.lib_registry[library]
        
        # Get the appropriate URL for the current system
        if "all" in lib_info["urls"]:
            url = lib_info["urls"]["all"].format(version=version)
            extract_func = lib_info["extract"]["all"]
        else:
            url = lib_info["urls"][self.system].format(version=version)
            extract_func = lib_info["extract"][self.system]

        # Download and extract
        lib_dir = Path("libs") / library
        lib_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            self._download_file(url, temp_file.name)
            extract_func(temp_file.name, str(lib_dir))
            logger.info(f"Installed {library} {version}")
        finally:
            os.unlink(temp_file.name)

    def _download_file(self, url: str, dest_path: str):
        """Download a file with progress bar."""
        try:
            with urllib.request.urlopen(url) as response:
                total_size = int(response.headers.get('content-length', 0))
                
                with open(dest_path, 'wb') as f:
                    with tqdm.tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            pbar.update(len(chunk))
        except urllib.error.URLError as e:
            logger.error(f"Failed to download {url}: {e}")
            sys.exit(1)

    def new(self, template: Optional[str] = None):
        """Create a new project template."""
        if Path("pockage.json").exists():
            logger.error("pockage.json already exists in this directory")
            sys.exit(1)

        template_config = {
            "name": Path.cwd().name,
            "version": "0.1.0",
            "description": "A new project built with Pockage!",
            "dependencies": {
                "sdl2": "2.28.5"
            },
            "platforms": {
                "macos": {
                    "enabled": True,
                    "build": {
                        "compiler": "clang++",
                        "cpp_version": "c++17",
                        "output": f"build/macos/{Path.cwd().name}",
                        "include_paths": ["include", "libs/sdl2/SDL2.framework/Headers"],
                        "frameworks": ["SDL2"],
                        "framework_paths": ["libs/sdl2"],
                        "build_flags": "-Wall -Wextra"
                    }
                },
                "windows": {
                    "enabled": False,
                    "build": {
                        "compiler": "g++",
                        "cpp_version": "c++17",
                        "output": f"build/windows/{Path.cwd().name}.exe",
                        "include_paths": ["include", "libs/sdl2/include"],
                        "lib_paths": ["libs/sdl2/lib"],
                        "link_libraries": ["SDL2"],
                        "build_flags": "-Wall -Wextra"
                    }
                },
                "linux": {
                    "enabled": False,
                    "build": {
                        "compiler": "g++",
                        "cpp_version": "c++17",
                        "output": f"build/linux/{Path.cwd().name}",
                        "include_paths": ["include", "libs/sdl2/include"],
                        "lib_paths": ["libs/sdl2/lib"],
                        "link_libraries": ["SDL2"],
                        "build_flags": "-Wall -Wextra"
                    }
                },
                "ios": {
                    "enabled": False,
                    "build": {
                        "compiler": "clang++",
                        "cpp_version": "c++17",
                        "output": f"build/ios/{Path.cwd().name}",
                        "include_paths": ["include", "libs/sdl2/SDL2.framework/Headers"],
                        "frameworks": ["SDL2"],
                        "framework_paths": ["libs/sdl2"],
                        "build_flags": "-Wall -Wextra -arch arm64 -isysroot $(xcrun --sdk iphoneos --show-sdk-path)"
                    }
                },
                "android": {
                    "enabled": False,
                    "build": {
                        "compiler": "clang++",
                        "cpp_version": "c++17",
                        "output": f"build/android/lib{Path.cwd().name}.so",
                        "include_paths": ["include", "libs/sdl2/include"],
                        "lib_paths": ["libs/sdl2/lib/${ANDROID_ABI}"],
                        "link_libraries": ["SDL2"],
                        "build_flags": "-Wall -Wextra -fPIC -shared"
                    }
                }
            },
            "run": {
                "executable": f"build/{self.system}/{Path.cwd().name}"
            }
        }

        # Create project structure
        Path("src").mkdir(exist_ok=True)
        Path("include").mkdir(exist_ok=True)
        Path("libs").mkdir(exist_ok=True)
        Path("build").mkdir(exist_ok=True)

        # Create basic files
        with open("pockage.json", "w") as f:
            json.dump(template_config, f, indent=2)

        with open("src/main.cpp", "w") as f:
            f.write("""#include <iostream>

int main() {
    std::cout << "Hello, Pockage!" << std::endl;
    return 0;
}
""")

        logger.info("Project created successfully!")

    def make(self, directory: str = "."):
        """Create a new project in the specified directory."""
        if directory != ".":
            Path(directory).mkdir(parents=True, exist_ok=True)
            os.chdir(directory)
        self.new()

    def install(self, library: Optional[str] = None):
        """Install specified library or all dependencies."""
        if not self.config:
            logger.error("No pockage.json found. Run 'pockage new' first.")
            sys.exit(1)

        if library:
            self._install_library(library)
        else:
            for lib, version in self.config["dependencies"].items():
                self._install_library(lib)

    def uninstall(self, library: str):
        """Remove a specific dependency."""
        if library not in self.config.get("dependencies", {}):
            logger.error(f"Library {library} not found in dependencies")
            sys.exit(1)

        lib_dir = Path("libs") / library
        if lib_dir.exists():
            shutil.rmtree(lib_dir)
            logger.info(f"Removed {library} from libs/")
        
        del self.config["dependencies"][library]
        with open("pockage.json", "w") as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Removed {library} from dependencies")

    def info(self):
        """Show project information."""
        if not self.config:
            logger.error("No pockage.json found. Run 'pockage new' first.")
            sys.exit(1)

        print("\nProject Information:")
        print(f"Name: {self.config['name']}")
        print(f"Version: {self.config['version']}")
        print(f"Description: {self.config.get('description', 'No description')}")
        
        print("\nDependencies:")
        for lib, version in self.config["dependencies"].items():
            print(f"  - {lib}: {version}")

        print("\nBuild Configuration:")
        print(f"  Compiler: {self.config['build']['compiler']}")
        print(f"  C++ Version: {self.config['build']['cpp_version']}")
        print(f"  Output: {self.config['build']['output']}")

    def search(self, query: str):
        """Search for available libraries."""
        matches = []
        for lib in self.lib_registry:
            if query.lower() in lib.lower():
                matches.append(lib)
        
        if matches:
            print("\nAvailable libraries:")
            for lib in matches:
                print(f"  - {lib}")
        else:
            print(f"No libraries found matching '{query}'")

    def doctor(self):
        """Check system setup."""
        print("\nSystem Check:")
        
        # Check Python version
        python_version = sys.version.split()[0]
        print(f"Python: {python_version} ✓")

        # Check compiler
        try:
            compiler = self.config.get("build", {}).get("compiler", "g++")
            result = subprocess.run([compiler, "--version"], capture_output=True, text=True)
            print(f"Compiler ({compiler}): {result.stdout.splitlines()[0]} ✓")
        except FileNotFoundError:
            print(f"Compiler ({compiler}): Not found ✗")

        # Check permissions
        print(f"Write permissions: {'✓' if os.access('.', os.W_OK) else '✗'}")

        # Check required directories
        required_dirs = ["src", "include", "libs", "build"]
        for dir_name in required_dirs:
            exists = Path(dir_name).exists()
            print(f"Directory {dir_name}: {'✓' if exists else '✗'}")

    def config_set(self, key: str, value: str):
        """Set global or project-specific configuration."""
        if "." in key:
            # Project-specific config
            if not self.config:
                logger.error("No pockage.json found. Run 'pockage new' first.")
                sys.exit(1)
            
            section, subkey = key.split(".", 1)
            if section not in self.config:
                self.config[section] = {}
            self.config[section][subkey] = value
            
            with open("pockage.json", "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Set {key} = {value} in pockage.json")
        else:
            # Global config
            self.global_config[key] = value
            self._save_global_config()
            logger.info(f"Set {key} = {value} in global config")

    def version(self):
        """Show Pockage version."""
        try:
            version = pkg_resources.get_distribution("pockage").version
            print(f"Pockage version: {version}")
        except pkg_resources.DistributionNotFound:
            print("Pockage version: development")

    def build(self):
        """Build the project."""
        if not self.config:
            logger.error("No pockage.json found. Run 'pockage new' first.")
            sys.exit(1)

        if "platforms" not in self.config:
            logger.error("No platform configurations found in pockage.json")
            sys.exit(1)

        # Get current platform configuration
        platform_config = self.config["platforms"].get(self.system)
        if not platform_config:
            logger.error(f"No configuration found for platform: {self.system}")
            sys.exit(1)

        if not platform_config.get("enabled", False):
            logger.error(f"Platform {self.system} is not enabled in configuration")
            sys.exit(1)

        build_config = platform_config["build"]
        compiler = build_config["compiler"]
        cpp_version = build_config["cpp_version"]
        output = build_config["output"]
        include_paths = build_config["include_paths"]
        build_flags = build_config["build_flags"]

        # Create output directory
        Path(output).parent.mkdir(parents=True, exist_ok=True)

        # Find all source files
        source_files = []
        for ext in ["cpp", "cxx", "cc", "c"]:
            source_files.extend(glob.glob(f"src/**/*.{ext}", recursive=True))

        if not source_files:
            logger.error("No source files found in src/ directory")
            sys.exit(1)

        # Platform-specific build command construction
        cmd = [compiler, f"-std={cpp_version}", *[f"-I{path}" for path in include_paths]]

        # Add framework paths and frameworks for macOS/iOS
        if self.system in ["macos", "ios"]:
            if "framework_paths" in build_config:
                cmd.extend(f"-F{path}" for path in build_config["framework_paths"])
            if "frameworks" in build_config:
                cmd.extend(f"-framework {framework}" for framework in build_config["frameworks"])
        else:
            # Add library paths and libraries for other platforms
            if "lib_paths" in build_config:
                cmd.extend(f"-L{path}" for path in build_config["lib_paths"])
            if "link_libraries" in build_config:
                cmd.extend(f"-l{lib}" for lib in build_config["link_libraries"])

        # Add build flags, source files and output
        cmd.extend([
            build_flags,
            *source_files,
            "-o", output
        ])

        # Run build
        try:
            subprocess.run(cmd, check=True)
            logger.info(f"Build successful: {output}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Build failed: {e}")
            sys.exit(1)

    def run(self):
        """Run the project."""
        if not self.config:
            logger.error("No pockage.json found. Run 'pockage new' first.")
            sys.exit(1)

        executable = self.config["run"]["executable"]
        if not Path(executable).exists():
            logger.error(f"Executable not found: {executable}")
            sys.exit(1)

        try:
            subprocess.run([executable], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Run failed: {e}")
            sys.exit(1)

    def clean(self):
        """Clean build artifacts."""
        if Path("build").exists():
            shutil.rmtree("build")
            logger.info("Cleaned build directory")
        else:
            logger.info("No build directory found")

    def update(self):
        """Update dependencies."""
        if not self.config:
            logger.error("No pockage.json found. Run 'pockage new' first.")
            sys.exit(1)

        for lib in self.config["dependencies"]:
            self._install_library(lib)
        logger.info("All dependencies updated")

def main():
    parser = argparse.ArgumentParser(description="Pockage - Simple C++ Package Manager & Build Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # New command
    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("template", nargs="?", help="Project template to use")

    # Make command
    make_parser = subparsers.add_parser("make", help="Create a new project in directory")
    make_parser.add_argument("directory", nargs="?", default=".", help="Directory to create project in")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("library", nargs="?", help="Specific library to install")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove a dependency")
    uninstall_parser.add_argument("library", help="Library to remove")

    # Build command
    subparsers.add_parser("build", help="Build the project")

    # Run command
    subparsers.add_parser("run", help="Run the project")

    # Clean command
    subparsers.add_parser("clean", help="Clean build artifacts")

    # Update command
    subparsers.add_parser("update", help="Update dependencies")

    # Info command
    subparsers.add_parser("info", help="Show project information")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for libraries")
    search_parser.add_argument("query", help="Search query")

    # Doctor command
    subparsers.add_parser("doctor", help="Check system setup")

    # Config command
    config_parser = subparsers.add_parser("config", help="Set configuration")
    config_parser.add_argument("action", choices=["set"])
    config_parser.add_argument("key", help="Configuration key")
    config_parser.add_argument("value", help="Configuration value")

    # Version command
    subparsers.add_parser("version", help="Show Pockage version")

    args = parser.parse_args()
    pockage = PockageManager()

    if args.command == "new":
        pockage.new(args.template)
    elif args.command == "make":
        pockage.make(args.directory)
    elif args.command == "install":
        pockage.install(args.library)
    elif args.command == "uninstall":
        pockage.uninstall(args.library)
    elif args.command == "build":
        pockage.build()
    elif args.command == "run":
        pockage.run()
    elif args.command == "clean":
        pockage.clean()
    elif args.command == "update":
        pockage.update()
    elif args.command == "info":
        pockage.info()
    elif args.command == "search":
        pockage.search(args.query)
    elif args.command == "doctor":
        pockage.doctor()
    elif args.command == "config":
        if args.action == "set":
            pockage.config_set(args.key, args.value)
    elif args.command == "version":
        pockage.version()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()