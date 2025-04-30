# Advanced Features

This document covers advanced features and configurations available in Pockage for more complex project requirements.

## Platform-Specific Build Configurations

Pockage supports platform-specific build configurations, allowing you to target multiple platforms from a single project:

- **Automatic Platform Detection**: Automatically uses the correct configuration for your current platform
- **Platform-Specific Output**: Builds are placed in platform-specific directories (e.g., `build/macos/`, `build/windows/`)
- **Customizable Settings**: Each platform can have its own compiler, flags, and library paths

Example `pockage.json` configuration:

```json
{
  "platforms": {
    "macos": {
      "enabled": true,
      "build": {
        "compiler": "clang++",
        "cpp_version": "c++17",
        "output": "build/macos/myapp",
        "include_paths": ["include", "libs/sdl2/SDL2.framework/Headers"],
        "frameworks": ["SDL2"],
        "framework_paths": ["libs/sdl2"]
      }
    },
    "windows": {
      "enabled": false,
      "build": {
        "compiler": "g++",
        "cpp_version": "c++17",
        "output": "build/windows/myapp.exe",
        "include_paths": ["include", "libs/sdl2/include"],
        "lib_paths": ["libs/sdl2/lib"],
        "link_libraries": ["SDL2"]
      }
    }
  }
}
```

## Custom Build Flags

You can specify custom compiler and linker flags for each platform:

```json
{
  "platforms": {
    "macos": {
      "build": {
        "compiler_flags": ["-Wall", "-Wextra", "-O3"],
        "linker_flags": ["-rpath @executable_path/../Frameworks"]
      }
    }
  }
}
```

## Source File Patterns

By default, Pockage will compile all `.cpp` files in the `src` directory. You can customize this behavior by specifying source file patterns:

```json
{
  "build": {
    "source_patterns": ["src/**/*.cpp", "modules/**/*.cpp"],
    "exclude_patterns": ["src/tests/**/*.cpp"]
  }
}
```

## Custom Build Commands

For more complex build requirements, you can specify custom build commands:

```json
{
  "build": {
    "pre_build": ["python scripts/generate_assets.py"],
    "post_build": ["python scripts/package.py"]
  }
}
```

## Creating macOS App Bundles

Pockage can create macOS app bundles for your applications:

```json
{
  "platforms": {
    "macos": {
      "app_bundle": {
        "enabled": true,
        "display_name": "My Application",
        "bundle_identifier": "com.example.myapp",
        "version": "1.0.0",
        "copyright": "© 2023 Example Inc.",
        "icon": "assets/AppIcon.appiconset"
      }
    }
  }
}
```

## Custom Templates

Pockage includes built-in templates for different types of projects. You can also create your own templates:

1. Create a directory with your template files
2. Add a `template.json` file with template metadata
3. Use the template with `pockage new --template path/to/template`

Example `template.json`:

```json
{
  "name": "Custom Template",
  "description": "A custom project template",
  "dependencies": {
    "sdl2": "2.28.5"
  },
  "platforms": {
    "macos": { "enabled": true },
    "windows": { "enabled": true },
    "linux": { "enabled": true }
  }
}
```

## Environment Variables

Pockage respects several environment variables that can be used to customize its behavior:

- `POCKAGE_HOME`: Custom location for Pockage data
- `POCKAGE_REGISTRY`: Custom registry URL
- `POCKAGE_CACHE`: Custom cache directory

## Registry Customization

You can customize the registry sources used by Pockage:

```json
{
  "registry_sources": [
    "https://example.com/custom-registry.json",
    "https://raw.githubusercontent.com/Jaseunda/pockages/refs/heads/main/registry/supported.json"
  ]
}
```

## Next Steps

- Explore [Platform Support](PLATFORMS.md) for platform-specific details
- Check out the [Command Reference](API.md) for detailed command documentation