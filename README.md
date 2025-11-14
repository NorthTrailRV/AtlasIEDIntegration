# AtlasIED AZM8 Home Assistant Integration

A custom Home Assistant integration for the **AtlasIED AZM8** 8-Zone Audio Mixer, providing complete control over all 8 audio zones through the Home Assistant interface.

## Features

- 🎵 **8 Independent Zone Control**: Control all 8 zones as separate media player entities
- 🔊 **Volume Control**: Adjust volume levels (0-100%) for each zone
- 🔇 **Mute Control**: Mute/unmute individual zones
- ⚡ **Power Control**: Turn zones on/off independently
- 🎚️ **Source Selection**: Switch between 8 input sources per zone
- 🔄 **Automatic Updates**: Real-time status updates via polling
- 🖥️ **UI Configuration**: Easy setup through Home Assistant UI

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/atlasied_azm8` folder to your Home Assistant's `custom_components` directory
2. If the `custom_components` directory doesn't exist, create it in the same location as your `configuration.yaml`
3. Restart Home Assistant

## Configuration

### Through the UI (Recommended)

1. Navigate to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "AtlasIED AZM8"
4. Enter your device configuration:
   - **Host**: IP address or hostname of your AZM8 device
   - **Port**: Network port (default: 80)
   - **Name**: Friendly name for your device (default: "AtlasIED AZM8")
5. Click **Submit**

The integration will create 8 media player entities, one for each zone:
- `media_player.atlasied_azm8_zone_1`
- `media_player.atlasied_azm8_zone_2`
- ... through Zone 8

## Usage

### Control Zones

Each zone can be controlled independently through:

**Volume Control:**
```yaml
service: media_player.volume_set
target:
  entity_id: media_player.atlasied_azm8_zone_1
data:
  volume_level: 0.5  # 50% volume
```

**Mute/Unmute:**
```yaml
service: media_player.volume_mute
target:
  entity_id: media_player.atlasied_azm8_zone_1
data:
  is_volume_muted: true
```

**Power Control:**
```yaml
service: media_player.turn_on
target:
  entity_id: media_player.atlasied_azm8_zone_1
```

**Source Selection:**
```yaml
service: media_player.select_source
target:
  entity_id: media_player.atlasied_azm8_zone_1
data:
  source: "Input 3"
```

### Automations Example

```yaml
automation:
  - alias: "Morning Music in All Zones"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: media_player.turn_on
        target:
          entity_id:
            - media_player.atlasied_azm8_zone_1
            - media_player.atlasied_azm8_zone_2
      - service: media_player.select_source
        target:
          entity_id:
            - media_player.atlasied_azm8_zone_1
            - media_player.atlasied_azm8_zone_2
        data:
          source: "Input 1"
      - service: media_player.volume_set
        target:
          entity_id:
            - media_player.atlasied_azm8_zone_1
            - media_player.atlasied_azm8_zone_2
        data:
          volume_level: 0.3
```

## Device Configuration

### API Protocol

This integration communicates with the AtlasIED AZM8 using HTTP requests. Ensure that:
- Your AZM8 device is connected to your network
- The device's IP address is accessible from Home Assistant
- Any firewalls allow communication on the configured port

### Customizing the Integration

If your AZM8 uses a different API protocol or endpoints, you may need to modify the `coordinator.py` file to match your device's specific API implementation. The current implementation provides a standard HTTP-based interface that can be adapted.

## Supported Features

- ✅ Volume control (0-100%)
- ✅ Mute control
- ✅ Power on/off
- ✅ Source selection (8 inputs)
- ✅ Independent zone control
- ✅ Status polling

## Troubleshooting

### Connection Issues

If you cannot connect to the device:
1. Verify the IP address and port are correct
2. Check that the AZM8 is powered on and connected to the network
3. Ensure there are no firewall rules blocking communication
4. Check Home Assistant logs for detailed error messages

### Viewing Logs

Enable debug logging by adding this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.atlasied_azm8: debug
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/berapp/atlasied_azm8).

## Credits

Developed for the Home Assistant community to provide seamless integration with AtlasIED AZM8 audio equipment.
