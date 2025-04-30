# Supported Libraries

Pockage provides easy access to popular C/C++ libraries. This document lists the currently supported libraries and explains how to add new ones to the registry.

## Currently Supported Libraries

| Library | Version | License | Description |
|---------|---------|---------|-------------|
| [SDL2](https://www.libsdl.org/) | 2.28.5 | zlib | Cross-platform development library |
| [Dear ImGui](https://github.com/ocornut/imgui) | 1.89.9 | MIT | Bloat-free GUI for C++ |
| [FreeType](https://www.freetype.org/) | 2.13.2 | FreeType License | Font rendering library |
| [SFML](https://www.sfml-dev.org/) | 2.6.1 | zlib | Simple and Fast Multimedia Library |
| [GLFW](https://www.glfw.org/) | 3.4.0 | zlib/libpng | OpenGL/Vulkan window creation |
| [Bullet Physics](https://pybullet.org/) | 3.25 | zlib | 3D physics engine |
| [Assimp](https://www.assimp.org/) | 5.3.1 | BSD | 3D model loading |
| [OpenAL Soft](https://openal-soft.org/) | 1.23.1 | LGPL | 3D audio library |
| [Box2D](https://box2d.org/) | 2.4.1 | MIT | 2D physics engine |
| [RapidJSON](https://rapidjson.org/) | 1.1.0 | MIT | Fast JSON parser |
| [fmt](https://fmt.dev/) | 10.2.1 | MIT | Modern formatting library |
| [spdlog](https://github.com/gabime/spdlog) | 1.13.0 | MIT | Fast logging library |
| [EnTT](https://github.com/skypjack/entt) | 3.13.1 | MIT | Entity Component System |

## Using Libraries in Your Project

### Adding Libraries to Your Project

To add a library to your project, edit your `pockage.json` file and add it to the dependencies section:

```json
{
  "dependencies": {
    "sdl2": "2.28.5",
    "imgui": "1.89.9"
  }
}
```

Then run:

```bash
pockage install
```

### Removing Libraries

To remove a library from your project:

```bash
pockage uninstall sdl2
```

Or remove it from the dependencies section in your `pockage.json` file and run `pockage install`.

### Updating Libraries

To update all libraries to their latest versions:

```bash
pockage update
```

### Searching for Libraries

To search for available libraries:

```bash
pockage search sdl
```

## Registry System

Pockage uses a registry system to manage library information. The registry is loaded from multiple sources in the following order:

1. Local `pockage.json` file (project-specific registry)
2. Local `registry/supported.json` file
3. Remote GitHub registry (`https://raw.githubusercontent.com/Jaseunda/pockages/refs/heads/main/registry/supported.json`)
4. Built-in fallback registry

## Adding New Libraries to the Registry

To add support for a new library, you can:

1. Add it to your local `pockage.json` file (project-specific)
2. Create a pull request to add it to the official registry

### Local Registry Format

To add a library to your local `pockage.json` file, use the following format:

```json
{
  "registry": {
    "library_name": {
      "urls": {
        "windows": "https://example.com/library-windows.zip",
        "macos": "https://example.com/library-macos.zip",
        "linux": "https://example.com/library-linux.tar.gz"
      },
      "extract": {
        "windows": "extract_zip",
        "macos": "extract_zip",
        "linux": "extract_targz"
      }
    }
  }
}
```

### Official Registry Format

To add a library to the official registry, use the following format in `registry/supported.json`:

```json
{
  "library_name": {
    "name": "Library Name",
    "latest_version": "1.0.0",
    "versions": {
      "1.0.0": {
        "url_windows": "https://...",
        "url_macos": "https://...",
        "url_linux": "https://..."
      }
    },
    "description": "Library description",
    "license": "License name"
  }
}
```

### Pull Request Requirements

When submitting a pull request to add a new library, please include:

1. Library information in `registry/supported.json`
2. Download URLs for all supported platforms
3. Extraction method for the library
4. License information

## Next Steps

- Learn about [Advanced Features](ADVANCED.md) for more complex project configurations
- Explore [Platform Support](PLATFORMS.md) for platform-specific details