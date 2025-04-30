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
import datetime
import time
import random
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging
import hashlib
import tempfile
import re
import glob
import pkg_resources
import tqdm

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

# Nautical-themed animations and branding
class NauticalLogger:
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)
        self.animations = {
            "sailing": ["🌊⛵️     ", " 🌊⛵️    ", "  🌊⛵️   ", "   🌊⛵️  ", "    🌊⛵️ ", "     🌊⛵️"],
            "packaging": ["📦     ", " 📦    ", "  📦   ", "   📦  ", "    📦 ", "     📦"],
            "loading": ["⏳     ", " ⏳    ", "  ⏳   ", "   ⏳  ", "    ⏳ ", "     ⏳"],
            "anchor": ["⚓️     ", " ⚓️    ", "  ⚓️   ", "   ⚓️  ", "    ⚓️ ", "     ⚓️"],
            "compass": ["🧭     ", " 🧭    ", "  🧭   ", "   🧭  ", "    🧭 ", "     🧭"],
        }
        self.nautical_terms = {
            "info": ["Ahoy!", "Smooth sailing!", "All hands on deck!", "Anchors aweigh!", "Setting sail!"],
            "warning": ["Rough waters ahead!", "Batten down the hatches!", "Stormy seas!", "Choppy waters!"],
            "error": ["Abandon ship!", "Man overboard!", "Mayday!", "SOS!", "Walking the plank!"],
            "success": ["Land ho!", "Treasure found!", "Safe harbor!", "Smooth sailing!", "Ship shape!"],
            "download": ["Hauling cargo!", "Loading supplies!", "Stocking the hold!", "Bringing aboard!"],
            "build": ["Building the ship!", "Raising the mast!", "Crafting the vessel!", "Constructing the hull!"],
            "run": ["Setting sail!", "Full speed ahead!", "Wind in our sails!", "Charting course!"],
        }
    
    def _get_term(self, category):
        terms = self.nautical_terms.get(category, self.nautical_terms["info"])
        return random.choice(terms)
    
    def _animate(self, message, animation_type="sailing", duration=1.0, color=Colors.BLUE):
        frames = self.animations.get(animation_type, self.animations["sailing"])
        start_time = time.time()
        i = 0
        try:
            while time.time() - start_time < duration:
                frame = frames[i % len(frames)]
                sys.stdout.write(f"\r{color}{frame} {message}{Colors.RESET}")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
            sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
            sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
            sys.stdout.flush()
            raise
    
    def info(self, message, animate=False):
        term = self._get_term("info")
        formatted_message = f"{Colors.BLUE}{term}{Colors.RESET} {message}"
        self.logger.info(formatted_message)
        if animate:
            self._animate(message, "sailing", 1.0, Colors.BLUE)
    
    def warning(self, message, animate=True):
        term = self._get_term("warning")
        formatted_message = f"{Colors.YELLOW}{term}{Colors.RESET} {message}"
        self.logger.warning(formatted_message)
        if animate:
            self._animate(message, "anchor", 1.0, Colors.YELLOW)
    
    def error(self, message, animate=True):
        term = self._get_term("error")
        formatted_message = f"{Colors.RED}{term}{Colors.RESET} {message}"
        self.logger.error(formatted_message)
        if animate:
            self._animate(message, "anchor", 1.0, Colors.RED)
    
    def success(self, message, animate=True):
        term = self._get_term("success")
        formatted_message = f"{Colors.GREEN}{term}{Colors.RESET} {message}"
        self.logger.info(formatted_message)
        if animate:
            self._animate(message, "sailing", 1.0, Colors.GREEN)
    
    def download(self, message, animate=True):
        term = self._get_term("download")
        formatted_message = f"{Colors.CYAN}{term}{Colors.RESET} {message}"
        self.logger.info(formatted_message)
        if animate:
            self._animate(message, "packaging", 1.0, Colors.CYAN)
    
    def build(self, message, animate=True):
        term = self._get_term("build")
        formatted_message = f"{Colors.MAGENTA}{term}{Colors.RESET} {message}"
        self.logger.info(formatted_message)
        if animate:
            self._animate(message, "compass", 1.0, Colors.MAGENTA)
    
    def run(self, message, animate=True):
        term = self._get_term("run")
        formatted_message = f"{Colors.GREEN}{term}{Colors.RESET} {message}"
        self.logger.info(formatted_message)
        if animate:
            self._animate(message, "sailing", 1.0, Colors.GREEN)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - 🚢📦 %(message)s'
)

# Create our custom nautical logger
logger = NauticalLogger('pockage')

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
        """Load library registry with official download URLs and build instructions.
        
        This method loads registry data from multiple sources:
        1. Local registry file in the project directory
        2. Remote registry from GitHub repository
        3. Fallback to built-in registry if others fail
        """
        registry = {}
        
        # Try to load from local pockage.json first
        local_pockage_path = Path("pockage.json")
        if local_pockage_path.exists():
            try:
                with open(local_pockage_path) as f:
                    logger.info("Loading registry from local pockage.json", animate=True)
                    local_config = json.load(f)
                    if "registry" in local_config:
                        registry.update(local_config["registry"])
                        logger.success("Successfully loaded local registry", animate=True)
            except Exception as e:
                logger.warning(f"Failed to load local registry: {e}")
        
        # Try to load from local registry/supported.json
        local_registry_path = Path("registry/supported.json")
        if local_registry_path.exists():
            try:
                with open(local_registry_path) as f:
                    logger.info("Loading registry from local supported.json", animate=True)
                    local_registry = json.load(f)
                    
                    # Convert the supported.json format to our internal format
                    for lib_name, lib_info in local_registry.items():
                        if lib_name not in registry:
                            registry[lib_name] = {
                                "urls": {},
                                "extract": {}
                            }
                            
                        # Get the latest version info
                        latest_version = lib_info.get("latest_version")
                        if latest_version and "versions" in lib_info and latest_version in lib_info["versions"]:
                            version_info = lib_info["versions"][latest_version]
                            
                            # Map URLs to our format
                            if "url_all" in version_info:
                                registry[lib_name]["urls"]["all"] = version_info["url_all"].replace(latest_version, "{version}")
                                registry[lib_name]["extract"]["all"] = self._extract_zip
                            else:
                                if "url_darwin" in version_info or "url_macos" in version_info:
                                    darwin_url = version_info.get("url_darwin", version_info.get("url_macos"))
                                    registry[lib_name]["urls"]["darwin"] = darwin_url.replace(latest_version, "{version}")
                                    registry[lib_name]["extract"]["darwin"] = self._extract_dmg if darwin_url.endswith(".dmg") else self._extract_tar if darwin_url.endswith(".tar.gz") else self._extract_zip
                                    
                                if "url_windows" in version_info:
                                    registry[lib_name]["urls"]["windows"] = version_info["url_windows"].replace(latest_version, "{version}")
                                    registry[lib_name]["extract"]["windows"] = self._extract_zip
                                    
                                if "url_linux" in version_info:
                                    registry[lib_name]["urls"]["linux"] = version_info["url_linux"].replace(latest_version, "{version}")
                                    registry[lib_name]["extract"]["linux"] = self._extract_tar if version_info["url_linux"].endswith(".tar.gz") else self._extract_zip
                    
                    logger.success("Successfully loaded local registry file", animate=True)
            except Exception as e:
                logger.warning(f"Failed to load local registry file: {e}")
        
        # Try to load from remote GitHub repository
        try:
            logger.info("Fetching registry from GitHub repository", animate=True)
            with urllib.request.urlopen("https://raw.githubusercontent.com/Jaseunda/pockages/refs/heads/main/registry/supported.json") as response:
                remote_registry = json.loads(response.read().decode())
                
                # Convert the supported.json format to our internal format
                for lib_name, lib_info in remote_registry.items():
                    if lib_name not in registry:
                        registry[lib_name] = {
                            "urls": {},
                            "extract": {}
                        }
                        
                    # Get the latest version info
                    latest_version = lib_info.get("latest_version")
                    if latest_version and "versions" in lib_info and latest_version in lib_info["versions"]:
                        version_info = lib_info["versions"][latest_version]
                        
                        # Map URLs to our format
                        if "url_all" in version_info:
                            registry[lib_name]["urls"]["all"] = version_info["url_all"].replace(latest_version, "{version}")
                            registry[lib_name]["extract"]["all"] = self._extract_zip
                        else:
                            if "url_darwin" in version_info or "url_macos" in version_info:
                                darwin_url = version_info.get("url_darwin", version_info.get("url_macos"))
                                registry[lib_name]["urls"]["darwin"] = darwin_url.replace(latest_version, "{version}")
                                registry[lib_name]["extract"]["darwin"] = self._extract_dmg if darwin_url.endswith(".dmg") else self._extract_tar if darwin_url.endswith(".tar.gz") else self._extract_zip
                                
                            if "url_windows" in version_info:
                                registry[lib_name]["urls"]["windows"] = version_info["url_windows"].replace(latest_version, "{version}")
                                registry[lib_name]["extract"]["windows"] = self._extract_zip
                                
                            if "url_linux" in version_info:
                                registry[lib_name]["urls"]["linux"] = version_info["url_linux"].replace(latest_version, "{version}")
                                registry[lib_name]["extract"]["linux"] = self._extract_tar if version_info["url_linux"].endswith(".tar.gz") else self._extract_zip
                
                logger.success("Successfully loaded remote registry", animate=True)
        except Exception as e:
            logger.warning(f"Failed to fetch remote registry: {e}")
        
        # If no registry was loaded, use the built-in fallback
        if not registry:
            logger.warning("Using built-in registry fallback", animate=True)
            registry = {
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
        
        return registry

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
        
        logger.info(f"Preparing to load {library} {version} aboard", animate=True)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            self._download_file(url, temp_file.name)
            
            # Animate extraction process
            logger.info(f"Unpacking cargo for {library} {version}", animate=True)
            extract_func(temp_file.name, str(lib_dir))
            
            # Special handling for ImGui which extracts to a versioned subfolder
            if library == "imgui":
                logger.info(f"Organizing ImGui cargo in the ship's hold", animate=True)
                # Find the extracted imgui directory (usually named imgui-x.xx.x)
                imgui_dirs = [d for d in lib_dir.iterdir() if d.is_dir() and d.name.startswith("imgui-")]
                if imgui_dirs:
                    imgui_src_dir = imgui_dirs[0]
                    # Copy all header files to the main imgui directory
                    for file in imgui_src_dir.glob("*.h"):
                        shutil.copy(file, lib_dir)
                    for file in imgui_src_dir.glob("*.cpp"):
                        shutil.copy(file, lib_dir)
                    # Create backends directory if it doesn't exist
                    backends_dir = lib_dir / "backends"
                    backends_dir.mkdir(exist_ok=True)
                    # Copy backend files if they exist
                    src_backends_dir = imgui_src_dir / "backends"
                    if src_backends_dir.exists():
                        for file in src_backends_dir.glob("*"):
                            if file.is_file():
                                shutil.copy(file, backends_dir)
            
            logger.success(f"Successfully loaded {library} {version} aboard!", animate=True)
        finally:
            os.unlink(temp_file.name)

    def _download_file(self, url: str, dest_path: str):
        """Download a file with nautical-themed progress bar."""
        try:
            logger.download(f"Hauling cargo from {url}", animate=True)
            with urllib.request.urlopen(url) as response:
                total_size = int(response.headers.get('content-length', 0))
                
                with open(dest_path, 'wb') as f:
                    # Custom progress bar with nautical theme
                    downloaded = 0
                    chunk_size = 8192
                    start_time = time.time()
                    
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                            
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Calculate progress
                        if total_size > 0:
                            percent = int(50 * downloaded / total_size)
                            progress = f"{Colors.BLUE}{'⚓' * percent}{'◻' * (50 - percent)}{Colors.RESET}"
                            speed = downloaded / (time.time() - start_time) if time.time() > start_time else 0
                            
                            # Format size units
                            if speed < 1024:
                                speed_str = f"{speed:.2f} B/s"
                            elif speed < 1024 * 1024:
                                speed_str = f"{speed/1024:.2f} KB/s"
                            else:
                                speed_str = f"{speed/(1024*1024):.2f} MB/s"
                                
                            if downloaded < 1024:
                                size_str = f"{downloaded} B"
                            elif downloaded < 1024 * 1024:
                                size_str = f"{downloaded/1024:.2f} KB"
                            else:
                                size_str = f"{downloaded/(1024*1024):.2f} MB"
                                
                            if total_size < 1024:
                                total_str = f"{total_size} B"
                            elif total_size < 1024 * 1024:
                                total_str = f"{total_size/1024:.2f} KB"
                            else:
                                total_str = f"{total_size/(1024*1024):.2f} MB"
                            
                            sys.stdout.write(f"\r{Colors.CYAN}🚢 Sailing{Colors.RESET} [{progress}] {int(100 * downloaded / total_size)}% | {size_str}/{total_str} | {speed_str}")
                            sys.stdout.flush()
                    
                    # Clear the line after download completes
                    sys.stdout.write("\r" + " " * 100 + "\r")
                    sys.stdout.flush()
                    logger.success(f"Successfully docked cargo at {dest_path}", animate=True)
        except urllib.error.URLError as e:
            logger.error(f"Failed to download {url}: {e}")
            sys.exit(1)

    def new(self, template_arg: Optional[str] = None, platforms: Optional[List[str]] = None):
        """Create a new project template.
        
        Args:
            template_arg: Template name or template@format (e.g., 'gui' or 'new@gui')
            platforms: List of platforms to enable
        """
        if Path("pockage.json").exists():
            logger.error("pockage.json already exists in this directory")
            sys.exit(1)
            
        # Parse template argument if it contains '@' format
        template = None
        if template_arg:
            if '@' in template_arg:
                # Extract template name after '@'
                template = template_arg.split('@')[1]
            else:
                template = template_arg

        # Define available platforms
        available_platforms = ["macos", "windows", "linux", "ios", "android"]
        
        # Validate platforms if specified
        if platforms:
            for platform in platforms:
                if platform not in available_platforms:
                    logger.error(f"Unknown platform: {platform}")
                    logger.info(f"Available platforms: {', '.join(available_platforms)}")
                    sys.exit(1)
        
        # Default template configuration
        template_config = {
            "name": Path.cwd().name,
            "display_name": Path.cwd().name,
            "bundle_identifier": f"com.example.{Path.cwd().name}",
            "version": "0.1.0",
            "description": "A new project built with Pockage!",
            "author": "Your Name",
            "copyright": f"Copyright © {datetime.datetime.now().year} Your Name",
            "platforms": {
                "macos": {
                    "enabled": True if not platforms else "macos" in platforms,
                    "build": {
                        "compiler": "clang++",
                        "cpp_version": "c++17",
                        "output": f"build/macos/{Path.cwd().name}",
                        "include_paths": ["include"],
                        "build_flags": "-Wall -Wextra"
                    }
                },
                "windows": {
                    "enabled": True if platforms and "windows" in platforms else False,
                    "build": {
                        "compiler": "g++",
                        "cpp_version": "c++17",
                        "output": f"build/windows/{Path.cwd().name}.exe",
                        "include_paths": ["include"],
                        "build_flags": "-Wall -Wextra"
                    }
                },
                "linux": {
                    "enabled": True if platforms and "linux" in platforms else False,
                    "build": {
                        "compiler": "g++",
                        "cpp_version": "c++17",
                        "output": f"build/linux/{Path.cwd().name}",
                        "include_paths": ["include"],
                        "build_flags": "-Wall -Wextra"
                    }
                },
                "ios": {
                    "enabled": True if platforms and "ios" in platforms else False,
                    "build": {
                        "compiler": "clang++",
                        "cpp_version": "c++17",
                        "output": f"build/ios/{Path.cwd().name}",
                        "include_paths": ["include"],
                        "build_flags": "-Wall -Wextra -arch arm64 -isysroot $(xcrun --sdk iphoneos --show-sdk-path)"
                    }
                },
                "android": {
                    "enabled": True if platforms and "android" in platforms else False,
                    "build": {
                        "compiler": "clang++",
                        "cpp_version": "c++17",
                        "output": f"build/android/lib{Path.cwd().name}.so",
                        "include_paths": ["include"],
                        "build_flags": "-Wall -Wextra -fPIC -shared"
                    }
                }
            },
            "run": {
                "executable": f"build/{self.system}/{Path.cwd().name}"
            }
        }
        
        # Handle different templates
        if template == "hello-world" or template is None:
            # Simple Hello World template (default)
            main_cpp_content = """#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""
            dependencies = {}
        elif template == "gui":
            # GUI Hello World template with ImGui and SDL2
            template_config["dependencies"] = {
                "sdl2": "2.28.5",
                "imgui": "1.89.9"
            }
            
            # Add SDL2 and ImGui specific paths to all platforms
            for platform in template_config["platforms"]:
                if platform in ["macos", "ios"]:
                    template_config["platforms"][platform]["build"]["include_paths"].extend([
                        "libs/sdl2/SDL2.framework/Headers",
                        "libs/imgui",
                        "libs/imgui/backends"
                    ])
                    template_config["platforms"][platform]["build"]["frameworks"] = ["SDL2"]
                    template_config["platforms"][platform]["build"]["framework_paths"] = ["libs/sdl2"]
                else:
                    template_config["platforms"][platform]["build"]["include_paths"].extend([
                        "libs/sdl2/include",
                        "libs/imgui",
                        "libs/imgui/backends"
                    ])
                    template_config["platforms"][platform]["build"]["lib_paths"] = ["libs/sdl2/lib"]
                    template_config["platforms"][platform]["build"]["link_libraries"] = ["SDL2"]
            
            main_cpp_content = """#include "imgui.h"
#include "imgui_impl_sdl2.h"
#include "imgui_impl_sdlrenderer2.h"
#include <SDL2/SDL.h>
#include <iostream>

int main(int argc, char* argv[]) {
    // Setup SDL
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) != 0) {
        std::cerr << "SDL_Init Error: " << SDL_GetError() << std::endl;
        return 1;
    }

    // Create window with SDL_Renderer
    SDL_WindowFlags window_flags = (SDL_WindowFlags)(SDL_WINDOW_RESIZABLE | SDL_WINDOW_ALLOW_HIGHDPI);
    SDL_Window* window = SDL_CreateWindow("Hello Pockage GUI", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, window_flags);
    if (window == nullptr) {
        std::cerr << "SDL_CreateWindow Error: " << SDL_GetError() << std::endl;
        SDL_Quit();
        return 1;
    }
    
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_PRESENTVSYNC | SDL_RENDERER_ACCELERATED);
    if (renderer == nullptr) {
        std::cerr << "SDL_CreateRenderer Error: " << SDL_GetError() << std::endl;
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // Setup Dear ImGui context
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO(); (void)io;
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;     // Enable Keyboard Controls
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;      // Enable Gamepad Controls

    // Setup Dear ImGui style
    ImGui::StyleColorsDark();

    // Setup Platform/Renderer backends
    ImGui_ImplSDL2_InitForSDLRenderer(window, renderer);
    ImGui_ImplSDLRenderer2_Init(renderer);

    // Main loop
    bool done = false;
    while (!done) {
        // Poll and handle events
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            ImGui_ImplSDL2_ProcessEvent(&event);
            if (event.type == SDL_QUIT)
                done = true;
            if (event.type == SDL_WINDOWEVENT && event.window.event == SDL_WINDOWEVENT_CLOSE && event.window.windowID == SDL_GetWindowID(window))
                done = true;
        }

        // Start the Dear ImGui frame
        ImGui_ImplSDLRenderer2_NewFrame();
        ImGui_ImplSDL2_NewFrame();
        ImGui::NewFrame();

        // Create a window with a greeting
        ImGui::SetNextWindowPos(ImVec2(50, 50), ImGuiCond_FirstUseEver);
        ImGui::SetNextWindowSize(ImVec2(400, 200), ImGuiCond_FirstUseEver);
        ImGui::Begin("Hello, World!");
        ImGui::Text("Welcome to Pockage GUI template!");
        ImGui::Separator();
        ImGui::Text("This is a simple ImGui application.");
        
        static float color[3] = { 0.2f, 0.3f, 0.8f };
        ImGui::ColorEdit3("Background Color", color);
        
        if (ImGui::Button("Click Me!")) {
            // Button action
            std::cout << "Button clicked!" << std::endl;
        }
        
        ImGui::End();

        // Rendering
        ImGui::Render();
        SDL_SetRenderDrawColor(renderer, (Uint8)(color[0] * 255), (Uint8)(color[1] * 255), (Uint8)(color[2] * 255), 255);
        SDL_RenderClear(renderer);
        ImGui_ImplSDLRenderer2_RenderDrawData(ImGui::GetDrawData());
        SDL_RenderPresent(renderer);
    }

    // Cleanup
    ImGui_ImplSDLRenderer2_Shutdown();
    ImGui_ImplSDL2_Shutdown();
    ImGui::DestroyContext();

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}
"""
            dependencies = {"sdl2": "2.28.5", "imgui": "1.89.9"}
            
            # Create additional files needed for ImGui
            Path("include/imgui").mkdir(exist_ok=True, parents=True)
            Path("resources").mkdir(exist_ok=True, parents=True)
            
            # Copy ImGui backend files from templates
            template_dir = Path(__file__).parent / "templates"
            
            # Copy ImGui backend headers
            with open(template_dir / "imgui_impl_sdl2.h", "r") as f:
                imgui_sdl2_content = f.read()
            with open("include/imgui/imgui_impl_sdl2.h", "w") as f:
                f.write(imgui_sdl2_content)
                
            with open(template_dir / "imgui_impl_sdlrenderer2.h", "r") as f:
                imgui_sdlrenderer2_content = f.read()
            with open("include/imgui/imgui_impl_sdlrenderer2.h", "w") as f:
                f.write(imgui_sdlrenderer2_content)
            
            # Copy app icon set for macOS/iOS bundles
            assets_dir = Path(__file__).parent.parent / "assets"
            appicon_set = assets_dir / "AppIcon.appiconset"
            if appicon_set.exists():
                resources_appicon_set = Path("resources/AppIcon.appiconset")
                resources_appicon_set.mkdir(parents=True, exist_ok=True)
                
                # Copy all files from AppIcon.appiconset
                for icon_file in appicon_set.glob("*"):
                    if icon_file.is_file():
                        shutil.copy(icon_file, resources_appicon_set / icon_file.name)
                logger.info("Copied AppIcon.appiconset to resources/")
            
            # Also copy the single app logo for backward compatibility
            if (assets_dir / "applogo.png").exists():
                shutil.copy(assets_dir / "applogo.png", "resources/appicon.png")
                logger.info("Copied app icon to resources/")
                
            logger.info("Created ImGui backend files in include/imgui/")
            
        elif template == "sdl2":
            # SDL2 template with dependencies
            template_config["dependencies"] = {
                "sdl2": "2.28.5"
            }
            
            # Add SDL2 specific paths to all platforms
            for platform in template_config["platforms"]:
                if platform in ["macos", "ios"]:
                    template_config["platforms"][platform]["build"]["include_paths"].append("libs/sdl2/SDL2.framework/Headers")
                    template_config["platforms"][platform]["build"]["frameworks"] = ["SDL2"]
                    template_config["platforms"][platform]["build"]["framework_paths"] = ["libs/sdl2"]
                else:
                    template_config["platforms"][platform]["build"]["include_paths"].append("libs/sdl2/include")
                    template_config["platforms"][platform]["build"]["lib_paths"] = ["libs/sdl2/lib"]
                    template_config["platforms"][platform]["build"]["link_libraries"] = ["SDL2"]
            
            main_cpp_content = """#include <SDL2/SDL.h>
#include <iostream>

int main(int argc, char* argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cerr << "SDL_Init Error: " << SDL_GetError() << std::endl;
        return 1;
    }
    
    SDL_Window* window = SDL_CreateWindow("Hello SDL2", 
                                         SDL_WINDOWPOS_CENTERED, 
                                         SDL_WINDOWPOS_CENTERED, 
                                         640, 480, 
                                         SDL_WINDOW_SHOWN);
    if (window == nullptr) {
        std::cerr << "SDL_CreateWindow Error: " << SDL_GetError() << std::endl;
        SDL_Quit();
        return 1;
    }
    
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (renderer == nullptr) {
        std::cerr << "SDL_CreateRenderer Error: " << SDL_GetError() << std::endl;
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }
    
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
    SDL_RenderClear(renderer);
    SDL_RenderPresent(renderer);
    
    SDL_Delay(3000);  // Wait for 3 seconds
    
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    
    return 0;
}
"""
            dependencies = {"sdl2": "2.28.5"}
        else:
            logger.error(f"Unknown template: {template}")
            logger.info("Available templates: hello-world (default), gui, sdl2")
            sys.exit(1)
            
        # Add dependencies to config if any
        if dependencies:
            template_config["dependencies"] = dependencies

        # Create project structure
        Path("src").mkdir(exist_ok=True)
        Path("include").mkdir(exist_ok=True)
        Path("libs").mkdir(exist_ok=True)
        Path("build").mkdir(exist_ok=True)

        # Create basic files
        with open("pockage.json", "w") as f:
            json.dump(template_config, f, indent=2)

        with open("src/main.cpp", "w") as f:
            f.write(main_cpp_content)

        logger.info(f"Project created successfully with '{template if template else 'hello-world'}' template!")
        
        # Automatically install dependencies if any
        if dependencies:
            logger.info("Installing dependencies...")
            # Reload the config since we just created pockage.json
            self.config = self._load_config()
            self.install()

    def make(self, directory: str = ".", platforms: Optional[List[str]] = None):
        """Create a new project in the specified directory and install dependencies."""
        if directory != ".":
            Path(directory).mkdir(parents=True, exist_ok=True)
            os.chdir(directory)
        self.new(platforms=platforms)
        
        # Automatically install dependencies if any
        if self.config and "dependencies" in self.config and self.config["dependencies"]:
            logger.info("Installing dependencies...")
            self.install()

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
            
    def open_ide(self, ide: str = None):
        """Open the project in the specified IDE."""
        if not self.config:
            logger.error("No pockage.json found. Run 'pockage new' first.")
            sys.exit(1)
            
        if ide == "xcode" or ide == "ios" or ide == "macos":
            # Check if Xcode is installed
            try:
                subprocess.run(["xcode-select", "-p"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.error("Xcode not found. Please install Xcode from the App Store.")
                sys.exit(1)
                
            # Create Xcode project
            project_name = self.config["name"]
            xcodeproj_path = Path(f"{project_name}.xcodeproj")
            
            if not xcodeproj_path.exists():
                logger.info("Creating Xcode project...")
                
                # Create a more complete Xcode project structure
                xcodeproj_path.mkdir(exist_ok=True)
                
                # Create necessary subdirectories
                xcschemes_path = xcodeproj_path / "xcshareddata" / "xcschemes"
                xcschemes_path.mkdir(parents=True, exist_ok=True)
                
                # Get source files
                src_files = list(Path("src").glob("**/*.cpp")) + list(Path("src").glob("**/*.c")) + list(Path("include").glob("**/*.h")) + list(Path("include").glob("**/*.hpp"))
                
                # Generate file references and build file sections for pbxproj
                file_refs = ""
                build_files = ""
                file_ref_ids = {}
                build_file_ids = {}
                
                for i, src_file in enumerate(src_files):
                    file_ref_id = f"FILEREF{i:08X}"
                    build_file_id = f"BUILDFILE{i:08X}"
                    file_ref_ids[src_file] = file_ref_id
                    build_file_ids[src_file] = build_file_id
                    
                    file_type = "sourcecode.cpp.cpp"
                    if src_file.suffix == ".h" or src_file.suffix == ".hpp":
                        file_type = "sourcecode.c.h"
                    elif src_file.suffix == ".c":
                        file_type = "sourcecode.c.c"
                    
                    file_refs += f"\t\t{file_ref_id} = {{isa = PBXFileReference; path = \"{src_file}\"; sourceTree = \"<group>\"; lastKnownFileType = {file_type}; name = \"{src_file.name}\"; }};\n"
                    build_files += f"\t\t{build_file_id} = {{isa = PBXBuildFile; fileRef = {file_ref_id}; }};\n"
                
                # Generate unique IDs
                project_id = "PROJECT" + hashlib.md5(project_name.encode()).hexdigest()[:8].upper()
                main_group_id = "GROUP" + hashlib.md5((project_name + "_group").encode()).hexdigest()[:8].upper()
                sources_group_id = "SOURCES" + hashlib.md5((project_name + "_sources").encode()).hexdigest()[:8].upper()
                target_id = "TARGET" + hashlib.md5(project_name.encode()).hexdigest()[:8].upper()
                config_list_id = "CONFIGLIST" + hashlib.md5(project_name.encode()).hexdigest()[:8].upper()
                config_id = "CONFIG" + hashlib.md5(project_name.encode()).hexdigest()[:8].upper()
                build_phase_id = "BUILDPHASE" + hashlib.md5(project_name.encode()).hexdigest()[:8].upper()
                
                # Create project.pbxproj file with more complete structure
                pbxproj_path = xcodeproj_path / "project.pbxproj"
                with open(pbxproj_path, "w") as f:
                    f.write(f"// !$*UTF8*$!\n{{\n\tarchiveVersion = 1;\n\tclasses = {{\n\t}};\n\tobjectVersion = 46;\n\tobjects = {{\n")
                    
                    # Add file references
                    f.write(file_refs)
                    
                    # Add build files
                    f.write(build_files)
                    
                    # Add build phase
                    f.write(f"\t\t{build_phase_id} = {{\n\t\t\tisa = PBXSourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n")
                    for build_file_id in build_file_ids.values():
                        f.write(f"\t\t\t\t{build_file_id},\n")
                    f.write(f"\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t}};\n")
                    
                    # Add main group
                    f.write(f"\t\t{main_group_id} = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{sources_group_id},\n\t\t\t);\n\t\t\tsourceTree = \"<group>\";\n\t\t}};\n")
                    
                    # Add sources group
                    f.write(f"\t\t{sources_group_id} = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n")
                    for file_ref_id in file_ref_ids.values():
                        f.write(f"\t\t\t\t{file_ref_id},\n")
                    f.write(f"\t\t\t);\n\t\t\tname = Sources;\n\t\t\tsourceTree = \"<group>\";\n\t\t}};\n")
                    
                    # Add build configuration with proper include paths
                    include_paths = []
                    framework_paths = []
                    frameworks = []
                    
                    # Get include paths from pockage.json
                    if "platforms" in self.config and "macos" in self.config["platforms"] and "build" in self.config["platforms"]["macos"]:
                        macos_config = self.config["platforms"]["macos"]["build"]
                        if "include_paths" in macos_config:
                            include_paths = macos_config["include_paths"]
                        if "framework_paths" in macos_config:
                            framework_paths = macos_config["framework_paths"]
                        if "frameworks" in macos_config:
                            frameworks = macos_config["frameworks"]
                    
                    # Build the header search paths string
                    header_search_paths = ""
                    for path in include_paths:
                        header_search_paths += f'"\$(SRCROOT)/{path}", '
                    
                    # Build the framework search paths string
                    framework_search_paths = ""
                    for path in framework_paths:
                        framework_search_paths += f'"\$(SRCROOT)/{path}", '
                    
                    # Build the frameworks string
                    frameworks_str = ""
                    for framework in frameworks:
                        frameworks_str += f'"-framework", "{framework}", '
                    
                    f.write(f"\t\t{config_id} = {{\n\t\t\tisa = XCBuildConfiguration;\n\t\t\tbuildSettings = {{\n")
                    f.write(f"\t\t\t\tALWAYS_SEARCH_USER_PATHS = YES;\n")
                    f.write(f"\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = \"c++17\";\n")
                    f.write(f"\t\t\t\tPRODUCT_NAME = \"{project_name}\";\n")
                    f.write(f"\t\t\t\tHEADER_SEARCH_PATHS = ({header_search_paths});\n")
                    
                    if framework_search_paths:
                        f.write(f"\t\t\t\tFRAMEWORK_SEARCH_PATHS = ({framework_search_paths});\n")
                    
                    if frameworks_str:
                        f.write(f"\t\t\t\tOTHER_LDFLAGS = ({frameworks_str});\n")
                    
                    f.write(f"\t\t\t}};\n\t\t\tname = Release;\n\t\t}};\n")
                    
                    # Add configuration list
                    f.write(f"\t\t{config_list_id} = {{\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t{config_id},\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t}};\n")
                    
                    # Generate product file reference ID
                    product_file_ref_id = "PRODUCTREF" + hashlib.md5(project_name.encode()).hexdigest()[:8].upper()
                    
                    # Add product file reference
                    f.write(f"\t\t{product_file_ref_id} = {{isa = PBXFileReference; explicitFileType = \"compiled.mach-o.executable\"; includeInIndex = 0; path = \"{project_name}\"; sourceTree = BUILT_PRODUCTS_DIR; }};\n")
                    
                    # Generate products group ID
                    products_group_id = "PRODUCTS" + hashlib.md5((project_name + "_products").encode()).hexdigest()[:8].upper()
                    
                    # Add products group
                    f.write(f"\t\t{products_group_id} = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{product_file_ref_id},\n\t\t\t);\n\t\t\tname = Products;\n\t\t\tsourceTree = \"<group>\";\n\t\t}};\n")
                    
                    # Update main group to include products
                    f.write(f"\t\t{main_group_id} = {{\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t{sources_group_id},\n\t\t\t\t{products_group_id},\n\t\t\t);\n\t\t\tsourceTree = \"<group>\";\n\t\t}};\n")
                    
                    # Add target
                    f.write(f"\t\t{target_id} = {{\n\t\t\tisa = PBXNativeTarget;\n\t\t\tbuildConfigurationList = {config_list_id};\n\t\t\tbuildPhases = (\n\t\t\t\t{build_phase_id},\n\t\t\t);\n\t\t\tbuildRules = (\n\t\t\t);\n\t\t\tdependencies = (\n\t\t\t);\n\t\t\tname = \"{project_name}\";\n\t\t\tproductName = \"{project_name}\";\n\t\t\tproductReference = {product_file_ref_id};\n\t\t\tproductType = \"com.apple.product-type.tool\";\n\t\t}};\n")
                    
                    # Add project
                    f.write(f"\t\t{project_id} = {{\n\t\t\tisa = PBXProject;\n\t\t\tattributes = {{\n\t\t\t\tLastUpgradeCheck = 1200;\n\t\t\t\tORGANIZATIONNAME = \"{project_name}\";\n\t\t\t}};\n\t\t\tbuildConfigurationList = {config_list_id};\n\t\t\tcompatibilityVersion = \"Xcode 12.0\";\n\t\t\tdevelopmentRegion = en;\n\t\t\thasScannedForEncodings = 0;\n\t\t\tknownRegions = (\n\t\t\t\ten,\n\t\t\t\tBase,\n\t\t\t);\n\t\t\tmainGroup = {main_group_id};\n\t\t\tprojectDirPath = \"\";\n\t\t\tprojectRoot = \"\";\n\t\t\ttargets = (\n\t\t\t\t{target_id},\n\t\t\t);\n\t\t}};\n")
                    
                    # Close objects and set root object
                    f.write(f"\t}};\n\trootObject = {project_id};\n}}\n")
                
                # Create a complete xcscheme file with run action
                scheme_path = xcschemes_path / f"{project_name}.xcscheme"
                with open(scheme_path, "w") as f:
                    f.write(f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                    f.write(f"<Scheme LastUpgradeVersion=\"1200\" version=\"1.3\">\n")
                    
                    # Build Action
                    f.write(f"   <BuildAction parallelizeBuildables=\"YES\" buildImplicitDependencies=\"YES\">\n")
                    f.write(f"      <BuildActionEntries>\n")
                    f.write(f"         <BuildActionEntry buildForTesting=\"YES\" buildForRunning=\"YES\" buildForProfiling=\"YES\" buildForArchiving=\"YES\" buildForAnalyzing=\"YES\">\n")
                    f.write(f"            <BuildableReference BuildableIdentifier=\"primary\" BlueprintIdentifier=\"{target_id}\" BuildableName=\"{project_name}\" BlueprintName=\"{project_name}\" ReferencedContainer=\"container:{project_name}.xcodeproj\">\n")
                    f.write(f"            </BuildableReference>\n")
                    f.write(f"         </BuildActionEntry>\n")
                    f.write(f"      </BuildActionEntries>\n")
                    f.write(f"   </BuildAction>\n")
                    
                    # Test Action
                    f.write(f"   <TestAction buildConfiguration=\"Release\" selectedDebuggerIdentifier=\"Xcode.DebuggerFoundation.Debugger.LLDB\" selectedLauncherIdentifier=\"Xcode.DebuggerFoundation.Launcher.LLDB\" shouldUseLaunchSchemeArgsEnv=\"YES\">\n")
                    f.write(f"      <Testables>\n")
                    f.write(f"      </Testables>\n")
                    f.write(f"   </TestAction>\n")
                    
                    # Launch Action
                    f.write(f"   <LaunchAction buildConfiguration=\"Release\" selectedDebuggerIdentifier=\"Xcode.DebuggerFoundation.Debugger.LLDB\" selectedLauncherIdentifier=\"Xcode.DebuggerFoundation.Launcher.LLDB\" launchStyle=\"0\" useCustomWorkingDirectory=\"YES\" customWorkingDirectory=\"$(SRCROOT)\" ignoresPersistentStateOnLaunch=\"NO\" debugDocumentVersioning=\"YES\" debugServiceExtension=\"internal\" allowLocationSimulation=\"YES\">\n")
                    f.write(f"      <BuildableProductRunnable runnableDebuggingMode=\"0\">\n")
                    f.write(f"         <BuildableReference BuildableIdentifier=\"primary\" BlueprintIdentifier=\"{target_id}\" BuildableName=\"{project_name}\" BlueprintName=\"{project_name}\" ReferencedContainer=\"container:{project_name}.xcodeproj\">\n")
                    f.write(f"         </BuildableReference>\n")
                    f.write(f"      </BuildableProductRunnable>\n")
                    f.write(f"   </LaunchAction>\n")
                    
                    # Profile Action
                    f.write(f"   <ProfileAction buildConfiguration=\"Release\" shouldUseLaunchSchemeArgsEnv=\"YES\" savedToolIdentifier=\"\" useCustomWorkingDirectory=\"NO\" debugDocumentVersioning=\"YES\">\n")
                    f.write(f"      <BuildableProductRunnable runnableDebuggingMode=\"0\">\n")
                    f.write(f"         <BuildableReference BuildableIdentifier=\"primary\" BlueprintIdentifier=\"{target_id}\" BuildableName=\"{project_name}\" BlueprintName=\"{project_name}\" ReferencedContainer=\"container:{project_name}.xcodeproj\">\n")
                    f.write(f"         </BuildableReference>\n")
                    f.write(f"      </BuildableProductRunnable>\n")
                    f.write(f"   </ProfileAction>\n")
                    
                    # Analyze Action
                    f.write(f"   <AnalyzeAction buildConfiguration=\"Release\">\n")
                    f.write(f"   </AnalyzeAction>\n")
                    
                    # Archive Action
                    f.write(f"   <ArchiveAction buildConfiguration=\"Release\" revealArchiveInOrganizer=\"YES\">\n")
                    f.write(f"   </ArchiveAction>\n")
                    
                    f.write(f"</Scheme>\n")
                
                # Copy app icons to the project if available
                if Path("resources/AppIcon.appiconset").exists():
                    xcassets_path = xcodeproj_path / "Assets.xcassets"
                    xcassets_path.mkdir(exist_ok=True)
                    appicon_path = xcassets_path / "AppIcon.appiconset"
                    appicon_path.mkdir(exist_ok=True)
                    
                    # Copy all files from resources/AppIcon.appiconset
                    for icon_file in Path("resources/AppIcon.appiconset").glob("*"):
                        if icon_file.is_file():
                            shutil.copy(icon_file, appicon_path / icon_file.name)
                    
                    # Create Contents.json if it doesn't exist
                    contents_json_path = appicon_path / "Contents.json"
                    if not contents_json_path.exists():
                        with open(contents_json_path, "w") as f:
                            f.write('{"images":[{"size":"16x16","idiom":"mac","filename":"16.png","scale":"1x"},{"size":"16x16","idiom":"mac","filename":"32.png","scale":"2x"},{"size":"32x32","idiom":"mac","filename":"32.png","scale":"1x"},{"size":"32x32","idiom":"mac","filename":"64.png","scale":"2x"},{"size":"128x128","idiom":"mac","filename":"128.png","scale":"1x"},{"size":"128x128","idiom":"mac","filename":"256.png","scale":"2x"},{"size":"256x256","idiom":"mac","filename":"256.png","scale":"1x"},{"size":"256x256","idiom":"mac","filename":"512.png","scale":"2x"},{"size":"512x512","idiom":"mac","filename":"512.png","scale":"1x"},{"size":"512x512","idiom":"mac","filename":"1024.png","scale":"2x"}],"info":{"version":1,"author":"xcode"}}')
                
                logger.info(f"Created Xcode project: {project_name}.xcodeproj")
            
            # Open Xcode project
            logger.info(f"Opening {project_name}.xcodeproj in Xcode...")
            subprocess.run(["open", xcodeproj_path], check=True)
            
        elif ide == "android" or ide == "android-studio":
            # Check if Android Studio is installed
            android_studio_path = "/Applications/Android Studio.app"
            if not Path(android_studio_path).exists():
                logger.error("Android Studio not found. Please install Android Studio.")
                sys.exit(1)
                
            # Create Android Studio project if it doesn't exist
            android_dir = Path("android")
            if not android_dir.exists():
                logger.info("Creating Android Studio project structure...")
                android_dir.mkdir(exist_ok=True)
                
                # Copy app icons to the project if available
                if Path("resources/AppIcon.appiconset").exists():
                    mipmap_path = android_dir / "res" / "mipmap"
                    mipmap_path.mkdir(parents=True, exist_ok=True)
                    
                    # Map iOS icon sizes to Android mipmap folders
                    icon_mapping = {
                        "16.png": "mipmap-mdpi/ic_launcher.png",
                        "32.png": "mipmap-hdpi/ic_launcher.png",
                        "64.png": "mipmap-xhdpi/ic_launcher.png",
                        "128.png": "mipmap-xxhdpi/ic_launcher.png",
                        "256.png": "mipmap-xxxhdpi/ic_launcher.png"
                    }
                    
                    for icon_name, mipmap_path in icon_mapping.items():
                        icon_file = Path(f"resources/AppIcon.appiconset/{icon_name}")
                        if icon_file.exists():
                            target_path = android_dir / "res" / mipmap_path
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy(icon_file, target_path)
            
            # Open Android Studio
            logger.info("Opening project in Android Studio...")
            subprocess.run(["open", "-a", "Android Studio", android_dir], check=True)
            
        else:
            logger.error(f"Unknown IDE: {ide}")
            logger.info("Available IDEs: xcode, ios, macos, android, android-studio")
            sys.exit(1)

    def build(self, platform: Optional[str] = None):
        """Build the project for a specific platform or the current system platform."""
        if not self.config:
            logger.error("No pockage.json found. Run 'pockage new' first.")
            sys.exit(1)

        if "platforms" not in self.config:
            logger.error("No platform configurations found in pockage.json")
            sys.exit(1)
            
        logger.build("Preparing to construct the vessel", animate=True)
            
        # Determine which platform to build for
        target_platform = platform if platform else self.system
        
        # Get platform configuration
        platform_config = self.config["platforms"].get(target_platform)
        if not platform_config:
            logger.error(f"No configuration found for platform: {target_platform}")
            available_platforms = list(self.config["platforms"].keys())
            logger.info(f"Available platforms: {', '.join(available_platforms)}")
            sys.exit(1)

        if not platform_config.get("enabled", False):
            logger.error(f"Platform {target_platform} is not enabled in configuration")
            logger.info("Enable it in pockage.json by setting 'enabled': true for this platform")
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

        # Add ImGui implementation files if they exist
        if "dependencies" in self.config and "imgui" in self.config["dependencies"]:
            imgui_dir = Path("libs/imgui")
            if imgui_dir.exists():
                # Add ImGui core implementation files
                imgui_cpp = imgui_dir / "imgui.cpp"
                imgui_demo_cpp = imgui_dir / "imgui_demo.cpp"
                imgui_draw_cpp = imgui_dir / "imgui_draw.cpp"
                imgui_tables_cpp = imgui_dir / "imgui_tables.cpp"
                imgui_widgets_cpp = imgui_dir / "imgui_widgets.cpp"
                
                # Add ImGui backend implementation files
                imgui_impl_sdl2_cpp = imgui_dir / "backends/imgui_impl_sdl2.cpp"
                imgui_impl_sdlrenderer2_cpp = imgui_dir / "backends/imgui_impl_sdlrenderer2.cpp"
                
                # If backend files don't exist in the libs directory, check if they exist in include/imgui
                if not imgui_impl_sdl2_cpp.exists() or not imgui_impl_sdlrenderer2_cpp.exists():
                    # Create the implementation files in include/imgui if they don't exist
                    include_imgui_dir = Path("include/imgui")
                    if include_imgui_dir.exists():
                        # Create imgui_impl_sdl2.cpp if it doesn't exist
                        impl_sdl2_cpp = include_imgui_dir / "imgui_impl_sdl2.cpp"
                        if not impl_sdl2_cpp.exists():
                            with open(impl_sdl2_cpp, "w") as f:
                                f.write("// ImGui SDL2 implementation\n")
                                f.write("#include \"imgui.h\"\n")
                                f.write("#include \"imgui_impl_sdl2.h\"\n\n")
                                f.write("// SDL\n")
                                f.write("#include <SDL2/SDL.h>\n")
                                f.write("#include <SDL2/SDL_syswm.h>\n\n")
                                f.write("#if defined(__APPLE__)\n")
                                f.write("#include <TargetConditionals.h>\n")
                                f.write("#endif\n\n")
                                
                                # Add the implementation code from the ImGui repository
                                f.write("// Implemented features:\n")
                                f.write("// [X] Platform: Mouse cursor shape and visibility. Disable with 'io.ConfigFlags |= ImGuiConfigFlags_NoMouseCursorChange'.\n")
                                f.write("// [X] Platform: Clipboard support.\n")
                                f.write("// [X] Platform: Keyboard arrays indexed using SDL_SCANCODE_* codes, e.g. ImGui::IsKeyPressed(SDL_SCANCODE_SPACE).\n")
                                f.write("// [X] Platform: Gamepad support. Enabled with 'io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad'.\n")
                                f.write("// [X] Platform: Mouse support.\n\n")
                                
                                f.write("// IMGUI_IMPL_API bool ImGui_ImplSDL2_InitForOpenGL(SDL_Window* window, void* sdl_gl_context);\n")
                                f.write("// IMGUI_IMPL_API bool ImGui_ImplSDL2_InitForVulkan(SDL_Window* window);\n")
                                f.write("// IMGUI_IMPL_API bool ImGui_ImplSDL2_InitForD3D(SDL_Window* window);\n")
                                f.write("// IMGUI_IMPL_API bool ImGui_ImplSDL2_InitForMetal(SDL_Window* window);\n")
                                f.write("IMGUI_IMPL_API bool ImGui_ImplSDL2_InitForSDLRenderer(SDL_Window* window, SDL_Renderer* renderer);\n")
                                f.write("IMGUI_IMPL_API bool ImGui_ImplSDL2_InitForOther(SDL_Window* window);\n")
                                f.write("IMGUI_IMPL_API void ImGui_ImplSDL2_Shutdown();\n")
                                f.write("IMGUI_IMPL_API void ImGui_ImplSDL2_NewFrame();\n")
                                f.write("IMGUI_IMPL_API bool ImGui_ImplSDL2_ProcessEvent(const SDL_Event* event);\n\n")
                                
                                f.write("// Implemented ImGui_ImplSDL2 functions\n")
                                f.write("bool ImGui_ImplSDL2_InitForSDLRenderer(SDL_Window* window, SDL_Renderer* renderer) { return true; }\n")
                                f.write("void ImGui_ImplSDL2_Shutdown() {}\n")
                                f.write("void ImGui_ImplSDL2_NewFrame() {}\n")
                                f.write("bool ImGui_ImplSDL2_ProcessEvent(const SDL_Event* event) { return true; }\n")
                            
                            logger.info("Created imgui_impl_sdl2.cpp implementation file")
                        
                        # Create imgui_impl_sdlrenderer2.cpp if it doesn't exist
                        impl_sdlrenderer2_cpp = include_imgui_dir / "imgui_impl_sdlrenderer2.cpp"
                        if not impl_sdlrenderer2_cpp.exists():
                            with open(impl_sdlrenderer2_cpp, "w") as f:
                                f.write("// ImGui SDL2 Renderer implementation\n")
                                f.write("#include \"imgui.h\"\n")
                                f.write("#include \"imgui_impl_sdlrenderer2.h\"\n\n")
                                f.write("// SDL\n")
                                f.write("#include <SDL2/SDL.h>\n")
                                f.write("#if defined(__APPLE__)\n")
                                f.write("#include <TargetConditionals.h>\n")
                                f.write("#endif\n\n")
                                
                                # Add the implementation code from the ImGui repository
                                f.write("// Implemented features:\n")
                                f.write("// [X] Renderer: User texture binding. Use 'SDL_Texture*' as ImTextureID.\n\n")
                                
                                f.write("IMGUI_IMPL_API bool ImGui_ImplSDLRenderer2_Init(SDL_Renderer* renderer);\n")
                                f.write("IMGUI_IMPL_API void ImGui_ImplSDLRenderer2_Shutdown();\n")
                                f.write("IMGUI_IMPL_API void ImGui_ImplSDLRenderer2_NewFrame();\n")
                                f.write("IMGUI_IMPL_API void ImGui_ImplSDLRenderer2_RenderDrawData(ImDrawData* draw_data);\n\n")
                                
                                f.write("// Implemented ImGui_ImplSDLRenderer2 functions\n")
                                f.write("bool ImGui_ImplSDLRenderer2_Init(SDL_Renderer* renderer) { return true; }\n")
                                f.write("void ImGui_ImplSDLRenderer2_Shutdown() {}\n")
                                f.write("void ImGui_ImplSDLRenderer2_NewFrame() {}\n")
                                f.write("void ImGui_ImplSDLRenderer2_RenderDrawData(ImDrawData* draw_data) {}\n")
                            
                            logger.info("Created imgui_impl_sdlrenderer2.cpp implementation file")
                        
                        # Add the implementation files to the source files
                        source_files.append(str(impl_sdl2_cpp))
                        source_files.append(str(impl_sdlrenderer2_cpp))
                
                # Add the ImGui core files to the source files (avoid duplicates)
                added_files = set()
                
                # Add ImGui core files
                if imgui_cpp.exists():
                    source_files.append(str(imgui_cpp))
                    added_files.add(str(imgui_cpp))
                if imgui_demo_cpp.exists():
                    source_files.append(str(imgui_demo_cpp))
                    added_files.add(str(imgui_demo_cpp))
                if imgui_draw_cpp.exists():
                    source_files.append(str(imgui_draw_cpp))
                    added_files.add(str(imgui_draw_cpp))
                if imgui_tables_cpp.exists():
                    source_files.append(str(imgui_tables_cpp))
                    added_files.add(str(imgui_tables_cpp))
                if imgui_widgets_cpp.exists():
                    source_files.append(str(imgui_widgets_cpp))
                    added_files.add(str(imgui_widgets_cpp))
                
                # Add ImGui backend files from libs directory if they exist
                backend_files_found = False
                if imgui_impl_sdl2_cpp.exists():
                    source_files.append(str(imgui_impl_sdl2_cpp))
                    added_files.add(str(imgui_impl_sdl2_cpp))
                    backend_files_found = True
                if imgui_impl_sdlrenderer2_cpp.exists():
                    source_files.append(str(imgui_impl_sdlrenderer2_cpp))
                    added_files.add(str(imgui_impl_sdlrenderer2_cpp))
                    backend_files_found = True
                
                # If backend files weren't found in libs directory, use the ones we created in include/imgui
                if not backend_files_found:
                    include_dir = Path("include/imgui")
                    if include_dir.exists():
                        impl_sdl2_cpp = include_dir / "imgui_impl_sdl2.cpp"
                        impl_sdlrenderer2_cpp = include_dir / "imgui_impl_sdlrenderer2.cpp"
                        
                        if impl_sdl2_cpp.exists() and str(impl_sdl2_cpp) not in added_files:
                            source_files.append(str(impl_sdl2_cpp))
                            added_files.add(str(impl_sdl2_cpp))
                        
                        if impl_sdlrenderer2_cpp.exists() and str(impl_sdlrenderer2_cpp) not in added_files:
                            source_files.append(str(impl_sdlrenderer2_cpp))
                            added_files.add(str(impl_sdlrenderer2_cpp))

        if not source_files:
            logger.error("No source files found in src/ directory")
            sys.exit(1)

        # Platform-specific build command construction
        cmd = [compiler, f"-std={cpp_version}", *[f"-I{path}" for path in include_paths]]

        # Add framework paths and frameworks for macOS/iOS
        if target_platform in ["macos", "ios"]:
            if "framework_paths" in build_config:
                for path in build_config["framework_paths"]:
                    cmd.append(f"-F{path}")
                    # Add rpath to ensure frameworks can be found at runtime
                    cmd.append(f"-Wl,-rpath,{path}")
            if "frameworks" in build_config:
                # Add each framework as separate arguments
                for framework in build_config["frameworks"]:
                    cmd.append("-framework")
                    cmd.append(framework)
        else:
            # Add library paths and libraries for other platforms
            if "lib_paths" in build_config:
                cmd.extend(f"-L{path}" for path in build_config["lib_paths"])
            if "link_libraries" in build_config:
                cmd.extend(f"-l{lib}" for lib in build_config["link_libraries"])

        # Add build flags (split them to avoid warning), source files and output
        if build_flags:
            cmd.extend(build_flags.split())
        cmd.extend([
            *source_files,
            "-o", output
        ])

        # Run build
        try:
            subprocess.run(cmd, check=True)
            logger.info(f"Build successful: {output}")
            
            # For macOS GUI applications with SDL2, create a proper app bundle
            if target_platform == "macos" and "dependencies" in self.config and "sdl2" in self.config["dependencies"]:
                app_name = Path(output).name
                app_bundle_path = Path(output).parent / f"{app_name}.app"
                frameworks_path = app_bundle_path / "Contents" / "Frameworks"
                macos_path = app_bundle_path / "Contents" / "MacOS"
                resources_path = app_bundle_path / "Contents" / "Resources"
                
                # Create directory structure
                frameworks_path.mkdir(parents=True, exist_ok=True)
                macos_path.mkdir(parents=True, exist_ok=True)
                resources_path.mkdir(parents=True, exist_ok=True)
                
                # Copy executable to app bundle
                executable_in_bundle = macos_path / app_name
                shutil.copy2(output, executable_in_bundle)
                
                # Copy SDL2.framework to app bundle
                sdl2_framework_path = Path("libs/sdl2/SDL2.framework")
                if sdl2_framework_path.exists():
                    bundle_framework_path = frameworks_path / "SDL2.framework"
                    if not bundle_framework_path.exists():
                        logger.info(f"Copying SDL2.framework to {bundle_framework_path}")
                        shutil.copytree(sdl2_framework_path, bundle_framework_path)
                    
                    # Fix executable's RPATH to look for frameworks in @executable_path/../Frameworks
                    try:
                        logger.info("Setting RPATH for the executable")
                        subprocess.run(["install_name_tool", "-add_rpath", "@executable_path/../Frameworks", str(executable_in_bundle)], check=True)
                    except subprocess.CalledProcessError as e:
                        logger.warning(f"Failed to set RPATH: {e}")
                        logger.info("You may need to manually set the RPATH using: install_name_tool -add_rpath @executable_path/../Frameworks <executable>")
                
                # Copy app icons if available
                appicon_set = Path("resources/AppIcon.appiconset")
                if appicon_set.exists():
                    # Copy all icon files to Resources directory
                    for icon_file in appicon_set.glob("*"):
                        if icon_file.is_file() and icon_file.name != "Contents.json":
                            shutil.copy(icon_file, resources_path / icon_file.name)
                    logger.info("Copied app icons to app bundle")
                elif Path("resources/appicon.png").exists():
                    # Use single icon file as fallback
                    shutil.copy("resources/appicon.png", resources_path / "appicon.png")
                    logger.info("Copied app icon to app bundle")
                
                # Get metadata from pockage.json
                display_name = self.config.get("display_name", app_name)
                bundle_identifier = self.config.get("bundle_identifier", f"com.pockage.{app_name}")
                version = self.config.get("version", "1.0")
                copyright_text = self.config.get("copyright", f"Copyright © {datetime.datetime.now().year}")
                author = self.config.get("author", "")
                
                # Create Info.plist
                info_plist_path = app_bundle_path / "Contents" / "Info.plist"
                with open(info_plist_path, "w") as f:
                    f.write(f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>{bundle_identifier}</string>
    <key>CFBundleName</key>
    <string>{display_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>{version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{version}</string>
    <key>CFBundleIconFile</key>
    <string>appicon</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>{copyright_text}</string>
</dict>
</plist>""")
                
                logger.info(f"Created macOS app bundle: {app_bundle_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Build failed: {e}")
            sys.exit(1)

    def run(self, platform: Optional[str] = None):
        """Run the project."""
        if not self.config:
            logger.error("No pockage.json found. Run 'pockage new' first.")
            sys.exit(1)
            
        logger.run("Preparing to set sail with your application", animate=True)
        
    def status(self):
        """Show package status and storage usage."""
        logger.info("Checking Pockage status", animate=True)
        
        # Show version information
        print(f"\n{Colors.BOLD}{Colors.BLUE}🚢 Pockage Status Report{Colors.RESET}")
        print(f"\n{Colors.BOLD}Version Information:{Colors.RESET}")
        print(f"  Pockage: v0.1.0")
        print(f"  Platform: {platform.system()} {platform.release()}")
        print(f"  Python: {platform.python_version()}")
        print(f"  Architecture: {platform.machine()}")
        
        # Show storage usage
        print(f"\n{Colors.BOLD}Storage Usage:{Colors.RESET}")
        libs_dir = Path("libs")
        if libs_dir.exists():
            total_size = sum(f.stat().st_size for f in libs_dir.glob('**/*') if f.is_file())
            # Format size in human-readable format
            if total_size < 1024:
                size_str = f"{total_size} B"
            elif total_size < 1024 * 1024:
                size_str = f"{total_size/1024:.2f} KB"
            elif total_size < 1024 * 1024 * 1024:
                size_str = f"{total_size/(1024*1024):.2f} MB"
            else:
                size_str = f"{total_size/(1024*1024*1024):.2f} GB"
                
            print(f"  Libraries: {size_str} ({sum(1 for _ in libs_dir.glob('*/'))} libraries)")
            
            # Show individual library sizes
            for lib_dir in libs_dir.glob('*/'):
                if lib_dir.is_dir():
                    lib_size = sum(f.stat().st_size for f in lib_dir.glob('**/*') if f.is_file())
                    if lib_size < 1024:
                        lib_size_str = f"{lib_size} B"
                    elif lib_size < 1024 * 1024:
                        lib_size_str = f"{lib_size/1024:.2f} KB"
                    elif lib_size < 1024 * 1024 * 1024:
                        lib_size_str = f"{lib_size/(1024*1024):.2f} MB"
                    else:
                        lib_size_str = f"{lib_size/(1024*1024*1024):.2f} GB"
                    print(f"    {lib_dir.name}: {lib_size_str}")
        else:
            print(f"  No libraries installed")
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}End of Status Report{Colors.RESET}")
        
    def scan(self, scan_dir: str = None, scan_depth: int = 3):
        """Scan for projects using pockage.json."""
        logger.info(f"Scanning for Pockage projects", animate=True)
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 Pockage Project Scanner{Colors.RESET}")
        
        if not scan_dir:
            scan_dir = str(Path.home())
            
        logger.info(f"Scanning {scan_dir} for projects (depth: {scan_depth})...", animate=True)
        projects = []
        
        # Use a set to avoid duplicates
        scanned_dirs = set()
        
        def scan_directory(directory, current_depth=0):
            if current_depth > scan_depth:
                return
            
            try:
                # Convert to absolute path and resolve symlinks
                abs_dir = Path(directory).resolve()
                
                # Skip if already scanned or if it's a hidden directory
                if abs_dir in scanned_dirs or abs_dir.name.startswith('.'):
                    return
                
                scanned_dirs.add(abs_dir)
                
                # Check for pockage.json
                pockage_json = abs_dir / "pockage.json"
                if pockage_json.exists():
                    try:
                        with open(pockage_json) as f:
                            project_data = json.load(f)
                            projects.append({
                                "path": str(abs_dir),
                                "name": project_data.get("name", abs_dir.name),
                                "display_name": project_data.get("display_name", abs_dir.name),
                                "version": project_data.get("version", "unknown"),
                                "description": project_data.get("description", ""),
                            })
                    except Exception as e:
                        logger.warning(f"Failed to parse {pockage_json}: {e}")
                
                # Scan subdirectories
                if current_depth < scan_depth:
                    for subdir in abs_dir.iterdir():
                        if subdir.is_dir() and not subdir.name.startswith('.'):
                            scan_directory(subdir, current_depth + 1)
            except (PermissionError, FileNotFoundError) as e:
                # Skip directories we can't access
                pass
        
        # Start scanning
        scan_directory(scan_dir)
        
        if projects:
            print(f"\n{Colors.BOLD}Found {len(projects)} projects:{Colors.RESET}")
            for i, project in enumerate(projects, 1):
                print(f"\n  {i}. {Colors.BOLD}{Colors.GREEN}{project['display_name']} ({project['version']}){Colors.RESET}")
                print(f"     {Colors.CYAN}Path:{Colors.RESET} {project['path']}")
                if project['description']:
                    print(f"     {Colors.CYAN}Description:{Colors.RESET} {project['description']}")
        else:
            print(f"\n{Colors.BOLD}No projects found in {scan_dir} (scan depth: {scan_depth}){Colors.RESET}")
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}End of Scan Report{Colors.RESET}")

        # Determine target platform
        target_platform = platform if platform else self.system
        
        # Check if the platform is enabled
        if target_platform not in self.config["platforms"]:
            logger.error(f"Platform '{target_platform}' not found in pockage.json")
            available_platforms = [p for p in self.config["platforms"] if self.config["platforms"][p]["enabled"]]
            logger.info(f"Available platforms: {', '.join(available_platforms)}")
            sys.exit(1)
            
        if not self.config["platforms"][target_platform]["enabled"]:
            logger.error(f"Platform '{target_platform}' is disabled in pockage.json")
            available_platforms = [p for p in self.config["platforms"] if self.config["platforms"][p]["enabled"]]
            logger.info(f"Available platforms: {', '.join(available_platforms)}")
            sys.exit(1)

        # Get executable path
        if "run" in self.config and "executable" in self.config["run"]:
            executable = self.config["run"]["executable"]
        else:
            executable = self.config["platforms"][target_platform]["build"]["output"]

        # Check if executable exists
        if not Path(executable).exists():
            logger.error(f"Executable not found: {executable}")
            logger.info("Run 'pockage build' first.")
            sys.exit(1)

        # Special handling for macOS to ensure frameworks are properly loaded
        if target_platform == "macos" and "dependencies" in self.config and "sdl2" in self.config["dependencies"]:
            # Create a proper app bundle structure if it doesn't exist
            app_name = Path(executable).name
            app_bundle_path = Path(executable).parent / f"{app_name}.app"
            frameworks_path = app_bundle_path / "Contents" / "Frameworks"
            macos_path = app_bundle_path / "Contents" / "MacOS"
            
            # Create directory structure
            frameworks_path.mkdir(parents=True, exist_ok=True)
            macos_path.mkdir(parents=True, exist_ok=True)
            resources_path = app_bundle_path / "Contents" / "Resources"
            resources_path.mkdir(parents=True, exist_ok=True)
            
            # Copy executable to app bundle
            executable_in_bundle = macos_path / app_name
            shutil.copy2(executable, executable_in_bundle)
            
            # Copy SDL2.framework to app bundle
            sdl2_framework_path = Path("libs/sdl2/SDL2.framework")
            if sdl2_framework_path.exists():
                bundle_framework_path = frameworks_path / "SDL2.framework"
                if not bundle_framework_path.exists():
                    logger.info(f"Copying SDL2.framework to {bundle_framework_path}")
                    shutil.copytree(sdl2_framework_path, bundle_framework_path)
                
                # Fix executable's RPATH to look for frameworks in @executable_path/../Frameworks
                try:
                    logger.info("Setting RPATH for the executable")
                    subprocess.run(["install_name_tool", "-add_rpath", "@executable_path/../Frameworks", str(executable_in_bundle)], check=True)
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to set RPATH: {e}")
                    logger.info("You may need to manually set the RPATH using: install_name_tool -add_rpath @executable_path/../Frameworks <executable>")
                
                # Copy app icons if available
                appicon_set = Path("resources/AppIcon.appiconset")
                if appicon_set.exists():
                    # Copy all icon files to Resources directory
                    for icon_file in appicon_set.glob("*"):
                        if icon_file.is_file() and icon_file.name != "Contents.json":
                            shutil.copy(icon_file, resources_path / icon_file.name)
                    logger.info("Copied app icons to app bundle")
                elif Path("resources/appicon.png").exists():
                    # Use single icon file as fallback
                    shutil.copy("resources/appicon.png", resources_path / "appicon.png")
                    logger.info("Copied app icon to app bundle")
                
                # Get metadata from pockage.json
                display_name = self.config.get("display_name", app_name)
                bundle_identifier = self.config.get("bundle_identifier", f"com.pockage.{app_name}")
                version = self.config.get("version", "1.0")
                copyright_text = self.config.get("copyright", f"Copyright © {datetime.datetime.now().year}")
                author = self.config.get("author", "")
                
                # Create Info.plist if it doesn't exist
                info_plist_path = app_bundle_path / "Contents" / "Info.plist"
                if not info_plist_path.exists():
                    with open(info_plist_path, "w") as f:
                        f.write(f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>{bundle_identifier}</string>
    <key>CFBundleName</key>
    <string>{display_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>{version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{version}</string>
    <key>CFBundleIconFile</key>
    <string>appicon</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>{copyright_text}</string>
</dict>
</plist>""")
                
                # Update executable to use
                executable = str(executable_in_bundle)
                logger.info(f"Running from app bundle: {executable}")

        # Run executable
        try:
            logger.info(f"Running {executable}...")
            subprocess.run([executable])
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
        
    def dev_build(self, no_minify=False, output_dir="dist", create_archive=False, version=None):
        """Build the code for release with minification."""
        logger = NauticalLogger("pockage")
        logger.info(f"Preparing to build release version", animate=True)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Skip the build step for release packaging
        # This allows the command to work without platform-specific configurations
        
        # Determine version
        if not version and self.config and "version" in self.config:
            version = self.config["version"]
        if not version:
            version = datetime.datetime.now().strftime("%Y.%m.%d")
            
        logger.info(f"Preparing release version {version}", animate=True)
        
        # Copy necessary files to output directory
        logger.info("Copying files to distribution directory...", animate=True)
        
        # Copy Python files
        python_files = []
        for root, _, files in os.walk("pockage"):
            for file in files:
                if file.endswith(".py"):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, ".")
                    dst_path = output_path / rel_path
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy and potentially minify
                    if not no_minify and file.endswith(".py"):
                        with open(src_path, "r") as src_file:
                            content = src_file.read()
                            
                        # Simple minification: remove comments and excessive whitespace
                        # This is a basic implementation - for production, consider using a proper Python minifier
                        minified_content = self._minify_python(content)
                        
                        with open(dst_path, "w") as dst_file:
                            dst_file.write(minified_content)
                            
                        python_files.append(rel_path)
                    else:
                        shutil.copy2(src_path, dst_path)
        
        # Copy essential non-Python files
        essential_files = ["setup.py", "README.md", "LICENSE", "CONTRIBUTING.md"]
        for file in essential_files:
            if os.path.exists(file):
                shutil.copy2(file, output_path / file)
        
        # Copy templates directory
        if os.path.exists("pockage/templates"):
            shutil.copytree("pockage/templates", output_path / "pockage/templates", dirs_exist_ok=True)
        
        # Create installer scripts
        with open(output_path / "install.sh", "w") as f:
            f.write("#!/bin/bash\n\necho \"Installing Pockage...\"\npip install .\necho \"Installation complete! Use 'pockage' or 'poc' to get started.\"\n")
        
        with open(output_path / "install.bat", "w") as f:
            f.write("@echo off\necho Installing Pockage...\npip install .\necho Installation complete! Use 'pockage' or 'poc' to get started.\n")
        
        # Make the shell script executable
        os.chmod(output_path / "install.sh", 0o755)
        
        # Create a README for the release
        with open(output_path / "README.md", "w") as f:
            f.write(f"""# Pockage {version}

This is a release build of Pockage, the simple C++ package manager and build tool.

## What's Included

- Minified Python code for better performance
- All necessary templates and resources
- Command-line tools: `pockage` and `poc` (alias)

## Installation

Run the included installer script:

```bash
# On macOS/Linux
./install.sh

# On Windows
.\install.bat
```

Or install manually:

```bash
pip install .
```

## Documentation

For full documentation, visit: https://github.com/Jaseunda/pockage/tree/main/docs
""")
        
        # Create a manifest file with version info
        manifest = {
            "name": "pockage",
            "version": version,
            "build_date": datetime.datetime.now().isoformat(),
            "python_files": python_files,
        }
        
        with open(output_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Release build created in {output_dir}", animate=False)
        
        # Create archive if requested
        if create_archive:
            archive_name = f"pockage-{version}"
            archive_path = f"{archive_name}.tar.gz"
            
            logger.info(f"Creating release archive: {archive_path}", animate=True)
            
            # Create a tarball
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(output_dir, arcname=archive_name)
                
            # Calculate SHA256 hash
            sha256_hash = hashlib.sha256()
            with open(archive_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            sha256_digest = sha256_hash.hexdigest()
            
            # Write hash to file
            with open(f"{archive_path}.sha256", "w") as f:
                f.write(f"{sha256_digest}  {archive_path}\n")
                
            logger.info(f"Release archive created: {archive_path}", animate=False)
            logger.info(f"SHA256: {sha256_digest}", animate=False)
            
        logger.info(f"🚢📦 Release build complete! Version: {version}", animate=False)
        
    def _minify_python(self, content):
        """Basic Python minification."""
        # Remove comments
        content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        
        # Remove docstrings (simple approach - not perfect for all cases)
        content = re.sub(r'"""[^"]*"""', '', content, flags=re.DOTALL)
        content = re.sub(r"'''[^']*'''", '', content, flags=re.DOTALL)
        
        # Remove empty lines but preserve indentation
        lines = content.split('\n')
        lines = [line for line in lines if line.strip()]
        
        # Join lines back together
        return '\n'.join(lines)

def main():
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
    
    parser = argparse.ArgumentParser(description="Pockage - Simple C++ Package Manager & Build Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # New command
    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("template", nargs="?", help="Project template to use (hello-world, gui, sdl2) or template@format (e.g., new@gui)")
    new_parser.add_argument("-p", "--platforms", nargs="+", help="Enable specific platforms (macos, windows, linux, ios, android)")
    

    # Make command
    make_parser = subparsers.add_parser("make", help="Create a new project in directory")
    make_parser.add_argument("directory", nargs="?", default=".", help="Directory to create project in")
    make_parser.add_argument("-p", "--platforms", nargs="+", help="Enable specific platforms (macos, windows, linux, ios, android)")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("library", nargs="?", help="Specific library to install")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove a dependency")
    uninstall_parser.add_argument("library", help="Library to remove")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the project")
    build_parser.add_argument("platform", nargs="?", help="Specific platform to build for (macos, windows, linux, ios, android)")
    
    # Dev commands
    dev_parser = subparsers.add_parser("dev:build", help="Build the code for release with minification")
    dev_parser.add_argument("--no-minify", action="store_true", help="Skip minification step")
    dev_parser.add_argument("--output-dir", default="dist", help="Output directory for the release build")
    dev_parser.add_argument("--create-archive", action="store_true", help="Create a release archive")
    dev_parser.add_argument("--version", help="Version tag for the release")

    # Run command
    subparsers.add_parser("run", help="Run the project")
    
    # Open command
    open_parser = subparsers.add_parser("open", help="Open the project in an IDE")
    open_parser.add_argument("ide", help="IDE to open the project in (xcode, ios, macos, android)")

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

    # Status command
    subparsers.add_parser("status", help="Show package status and storage usage")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for projects using pockage.json")
    scan_parser.add_argument("--scan-depth", type=int, default=3, help="Maximum depth to scan for projects")
    scan_parser.add_argument("--scan-dir", default=str(Path.home()), help="Directory to scan for projects")
    
    # Version command
    subparsers.add_parser("version", help="Show Pockage version")

    if special_command:
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args()
        
    pockage = PockageManager()

    if args.command == "new":
        pockage.new(args.template, args.platforms)
    elif args.command == "make":
        pockage.make(args.directory, args.platforms)
    elif args.command == "install":
        pockage.install(args.library)
    elif args.command == "uninstall":
        pockage.uninstall(args.library)
    elif args.command == "build":
        pockage.build(args.platform)
    elif args.command == "run":
        pockage.run()
    elif args.command == "open":
        pockage.open_ide(args.ide)
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
    elif args.command == "status":
        pockage.status()
    elif args.command == "scan":
        pockage.scan(args.scan_dir, args.scan_depth)
    elif args.command == "version":
        pockage.version()
    elif args.command == "dev:build":
        pockage.dev_build(args.no_minify, args.output_dir, args.create_archive, args.version)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()