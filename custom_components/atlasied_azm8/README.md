# AtlasIED AZM8 Home Assistant Integration

This directory contains a custom Home Assistant integration for the AtlasIED AZM8 8-Zone Audio Mixer.

## Quick Start

1. Copy the entire `custom_components/atlasied_azm8` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services → Add Integration → "AtlasIED AZM8"
4. Enter your device's IP address and port

## What's Included

- **8 Media Player Entities**: One for each zone of the AZM8
- **Full Control**: Volume, mute, power, and source selection
- **UI Configuration**: Easy setup without editing YAML files
- **Automatic Polling**: Keeps zone status up to date

See [README.md](README.md) for complete documentation.
