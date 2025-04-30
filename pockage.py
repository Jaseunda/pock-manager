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
import requests
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pockage')

class PockageManager:
    def __init__(self):
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / '.pockage'
        self.cache_dir = self.config_dir / 'cache'
        self.config_file = self.config_dir / 'config.json'
        self.supported_file = Path(__file__).parent / 'registry' / 'supported.json'
        self._ensure_directories()
        self._load_config()
        self._load_supported_libraries()
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.lib_registry = self._load_lib_registry()
        self.global_config = self._load_global_config()

    def _ensure_directories(self):
        """Ensure all necessary directories exist."""
        self.config_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration file."""
        default_config = {
            "cache_dir": str(self.cache_dir),
            "compiler": "g++",
            "cpp_version": "c++17",
            "build_flags": "-Wall -Wextra",
            "parallel_build": True,
            "max_cache_size": "10GB"  # Default cache size limit
        }
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
            self._create_default_config()

    def _load_supported_libraries(self):
        """Load supported libraries from registry."""
        if self.supported_file.exists():
            with open(self.supported_file, 'r') as f:
                self.supported_libraries = json.load(f)
        else:
            self.supported_libraries = {}
            logging.error("Supported libraries file not found!")

    def _get_cache_path(self, library: str, version: str) -> Path:
        """Get the cache path for a specific library version."""
        return self.cache_dir / library / version

    def _is_cached(self, library: str, version: str) -> bool:
        """Check if a library version is cached."""
        cache_path = self._get_cache_path(library, version)
        return cache_path.exists() and any(cache_path.iterdir())

    def _cache_library(self, library: str, version: str, download_path: Path):
        """Cache a downloaded library."""
        cache_path = self._get_cache_path(library, version)
        cache_path.mkdir(parents=True, exist_ok=True)
        
        # Copy or move the downloaded files to cache
        if download_path.is_dir():
            shutil.copytree(download_path, cache_path, dirs_exist_ok=True)
        else:
            shutil.copy2(download_path, cache_path)

    def _symlink_from_cache(self, library: str, version: str, target_path: Path):
        """Create a symlink from cache to target path."""
        cache_path = self._get_cache_path(library, version)
        if not cache_path.exists():
            raise FileNotFoundError(f"Library {library} version {version} not found in cache")
        
        # Remove existing target if it exists
        if target_path.exists():
            if target_path.is_symlink():
                target_path.unlink()
            else:
                shutil.rmtree(target_path)
        
        # Create symlink
        target_path.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(cache_path, target_path, target_is_directory=True)

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
            "build": {
                "compiler": "g++",
                "cpp_version": "c++17",
                "output": f"build/{Path.cwd().name}",
                "include_paths": [
                    "include",
                    "libs/sdl2/include"
                ],
                "lib_paths": [
                    "libs/sdl2/lib"
                ],
                "link_libraries": [
                    "SDL2"
                ],
                "build_flags": "-Wall -Wextra"
            },
            "run": {
                "executable": f"build/{Path.cwd().name}"
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

    def _install_library(self, library: str):
        """Install a specific library."""
        if library not in self.lib_registry:
            logger.error(f"Library {library} not supported yet.")
            sys.exit(1)

        version = self.config["dependencies"][library]
        lib_dir = Path("libs") / library
        lib_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Installing {library} {version}...")
        
        lib_info = self.lib_registry[library]
        url_template = lib_info["urls"].get(self.system, lib_info["urls"].get("all"))
        if not url_template:
            logger.error(f"No download URL available for {library} on {self.system}")
            sys.exit(1)

        url = url_template.format(version=version)
        self._download_and_extract(url, lib_dir, lib_info["extract"].get(self.system, lib_info["extract"]["all"]))

    def _download_and_extract(self, url: str, target_dir: Path, extract_func):
        """Download and extract a library archive."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            logger.info(f"Downloading {url}...")
            try:
                urllib.request.urlretrieve(url, tmp_file.name)
                extract_func(tmp_file.name, target_dir)
            except Exception as e:
                logger.error(f"Failed to download/extract: {e}")
                sys.exit(1)
            finally:
                os.unlink(tmp_file.name)

    def _extract_zip(self, archive: str, target_dir: Path):
        with zipfile.ZipFile(archive, 'r') as zip_ref:
            zip_ref.extractall(target_dir)

    def _extract_tar(self, archive: str, target_dir: Path):
        with tarfile.open(archive, 'r:gz') as tar_ref:
            tar_ref.extractall(target_dir)

    def _extract_dmg(self, archive: str, target_dir: Path):
        # macOS specific extraction
        subprocess.run(['hdiutil', 'attach', archive], check=True)
        try:
            # TODO: Implement proper DMG extraction
            pass
        finally:
            subprocess.run(['hdiutil', 'detach', '/Volumes/SDL2'], check=True)

    def build(self):
        """Build the project using parallel compilation."""
        if not self.config.get("build"):
            logger.error("No build configuration found in pockage.json")
            sys.exit(1)

        build_config = self.config["build"]
        compiler = build_config.get("compiler", "g++")
        cpp_version = build_config.get("cpp_version", "c++17")
        output = build_config.get("output", "build/output")
        build_flags = build_config.get("build_flags", "")

        # Create build directory
        Path("build").mkdir(exist_ok=True)

        # Find all source files
        src_files = list(Path("src").rglob("*.cpp"))
        if not src_files:
            logger.error("No source files found in src/ directory")
            sys.exit(1)

        # Prepare include paths
        include_flags = " ".join(f"-I{path}" for path in build_config.get("include_paths", []))
        lib_paths = " ".join(f"-L{path}" for path in build_config.get("lib_paths", []))
        link_libs = " ".join(f"-l{lib}" for lib in build_config.get("link_libraries", []))

        # Build command template
        cmd_template = [
            compiler,
            f"-std={cpp_version}",
            build_flags,
            include_flags,
            lib_paths,
            link_libs,
            "-c",  # Compile only
            "{}",  # Source file
            "-o", "build/{}.o"  # Object file
        ]

        # Parallel compilation
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for src_file in src_files:
                obj_file = f"build/{src_file.stem}.o"
                cmd = [x.format(src_file) for x in cmd_template]
                futures.append(executor.submit(self._compile_file, cmd))

            # Wait for all compilations to complete
            concurrent.futures.wait(futures)

        # Link all object files
        obj_files = [f"build/{f.stem}.o" for f in src_files]
        link_cmd = [
            compiler,
            *obj_files,
            lib_paths,
            link_libs,
            "-o", output
        ]

        logger.info("Linking...")
        try:
            subprocess.run(link_cmd, check=True)
            logger.info(f"Build successful! Output: {output}")
        except subprocess.CalledProcessError:
            logger.error("Linking failed!")
            sys.exit(1)

    def _compile_file(self, cmd: List[str]):
        """Compile a single source file."""
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            logger.error(f"Compilation failed for {cmd[-2]}")
            sys.exit(1)

    def run(self):
        """Run the built executable."""
        if not self.config.get("run"):
            logger.error("No run configuration found in pockage.json")
            sys.exit(1)

        executable = self.config["run"].get("executable")
        if not executable:
            logger.error("No executable specified in pockage.json")
            sys.exit(1)

        if not Path(executable).exists():
            logger.error(f"Executable {executable} not found. Did you build the project?")
            sys.exit(1)

        logger.info(f"Running {executable}...")
        try:
            subprocess.run([executable], check=True)
        except subprocess.CalledProcessError:
            logger.error("Program execution failed!")
            sys.exit(1)

    def clean(self):
        """Clean build artifacts."""
        if Path("build").exists():
            logger.info("Cleaning build directory...")
            shutil.rmtree("build")
            logger.info("Build directory cleaned.")
        else:
            logger.info("No build directory found.")

    def update(self):
        """Update all dependencies to their latest versions."""
        # TODO: Implement version checking and updating
        logger.info("Update functionality coming soon!")

    def cache_list(self):
        """List all cached libraries."""
        if not self.cache_dir.exists():
            logging.info("Cache directory is empty")
            return

        total_size = 0
        print("\nCached Libraries:")
        print("-" * 50)
        for library_dir in self.cache_dir.iterdir():
            if not library_dir.is_dir():
                continue
            print(f"\n{library_dir.name}:")
            for version_dir in library_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                size = sum(f.stat().st_size for f in version_dir.rglob('*') if f.is_file())
                total_size += size
                print(f"  - {version_dir.name}: {self._format_size(size)}")
        
        print("\nTotal cache size:", self._format_size(total_size))

    def cache_clean(self, library: Optional[str] = None, version: Optional[str] = None):
        """Clean the cache, optionally for a specific library or version."""
        if not self.cache_dir.exists():
            logging.info("Cache directory is empty")
            return

        if library:
            lib_dir = self.cache_dir / library
            if not lib_dir.exists():
                logging.error(f"Library {library} not found in cache")
                return

            if version:
                version_dir = lib_dir / version
                if version_dir.exists():
                    shutil.rmtree(version_dir)
                    logging.info(f"Removed {library} {version} from cache")
                else:
                    logging.error(f"Version {version} not found for {library}")
            else:
                shutil.rmtree(lib_dir)
                logging.info(f"Removed all versions of {library} from cache")
        else:
            # Clean entire cache
            for item in self.cache_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
            logging.info("Cleared entire cache")

    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

def main():
    parser = argparse.ArgumentParser(description="Pockage - The npm for C/C++")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")

    # New command
    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("template", nargs="?", help="Template to use (hello-world, gui, sdl2) or template@format (e.g., new@gui)")
    new_parser.add_argument("-p", "--platforms", nargs="+", help="Platforms to enable (macos, windows, linux, ios, android)")

    # Make command
    make_parser = subparsers.add_parser("make", help="Create a new project in a directory")
    make_parser.add_argument("directory", help="Directory to create the project in")
    make_parser.add_argument("-p", "--platforms", nargs="+", help="Platforms to enable (macos, windows, linux, ios, android)")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("library", nargs="?", help="Library to install")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove a dependency")
    uninstall_parser.add_argument("library", help="Library to uninstall")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show project information")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for libraries")
    search_parser.add_argument("query", help="Search query")

    # Doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Check system setup")

    # Config command
    config_parser = subparsers.add_parser("config-set", help="Set configuration")
    config_parser.add_argument("key", help="Configuration key")
    config_parser.add_argument("value", help="Configuration value")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the project")
    build_parser.add_argument("platform", nargs="?", help="Platform to build for (macos, windows, linux, ios, android)")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the project")

    # Clean command
    subparsers.add_parser("clean", help="Clean build artifacts")

    # Update command
    subparsers.add_parser("update", help="Update dependencies")

    # Cache command
    cache_parser = subparsers.add_parser("cache", help="Cache management")
    cache_parser.add_argument("action", choices=["list", "clean"])
    cache_parser.add_argument("library", nargs="?", help="Library to manage")
    cache_parser.add_argument("version", nargs="?", help="Version to manage")

    # Handle special command formats like new@gui
    argv = sys.argv[1:]
    special_command = None
    
    if len(argv) > 0 and '@' in argv[0] and not argv[0].startswith('-'):
        parts = argv[0].split('@')
        if len(parts) == 2:
            if parts[0] in ["new", "make"]:
                # Replace new@gui with new gui
                argv[0] = parts[0]
                argv.insert(1, parts[1])
                special_command = True
    
    if special_command:
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args()

    pockage = PockageManager()

    if args.command == "version":
        pockage.version()
    elif args.command == "new":
        pockage.new(args.template, args.platforms)
    elif args.command == "make":
        pockage.make(args.directory, args.platforms)
    elif args.command == "install":
        pockage.install(args.library)
    elif args.command == "uninstall":
        pockage.uninstall(args.library)
    elif args.command == "build":
        pockage.build(args.platform if 'platform' in args else None)
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
    elif args.command == "config-set":
        pockage.config_set(args.key, args.value)
    elif args.command == "cache":
        if args.action == "list":
            pockage.cache_list()
        elif args.action == "clean":
            pockage.cache_clean(args.library, args.version)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()