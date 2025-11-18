# AtlasIED AZM4/AZM8 Home Assistant Integration

This is a custom integration for Home Assistant to control AtlasIED AZM4 and AZM8 audio zone mixers.

## Features

- **Real-time Communication**: Uses TCP (port 5321) and UDP (port 3131) for bidirectional communication
- **Automatic Subscriptions**: Subscribes to device parameters and receives real-time updates
- **Keep-alive**: Maintains connection with automatic keep-alive messages every 4 minutes
- **Multiple Entity Types**:
  - **Number Entities**: Zone and Source gain controls (-80dB to +12dB)
  - **Switch Entities**: Zone and Source mute controls, Group combine/uncombine
  - **Sensor Entities**: Zone and Source names, audio meters (dB levels)

## Installation

1. Copy the `custom_components/atlasied_azm` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "+ Add Integration"
5. Search for "AtlasIED AZM4/AZM8"
6. Enter your device's IP address and configure the number of zones, sources, and groups

## Configuration

During setup, you'll need to provide:
- **Host IP Address**: The IP address of your AZM4/AZM8 device
- **Number of Zones**: Number of audio zones (1-16, default: 8)
- **Number of Sources**: Number of audio sources (1-16, default: 4)
- **Number of Groups**: Number of zone groups (1-8, default: 4)

## Usage

### Entities Created

For each zone (e.g., Zone 1):
- `number.zone_1_gain` - Volume control slider (-80 to +12 dB)
- `switch.zone_1_mute` - Mute on/off
- `sensor.zone_1_name` - Zone name from device
- `sensor.zone_1_meter` - Real-time audio level meter

For each source (e.g., Source 1):
- `number.source_1_gain` - Volume control slider (-80 to +12 dB)
- `switch.source_1_mute` - Mute on/off
- `sensor.source_1_name` - Source name from device
- `sensor.source_1_meter` - Real-time audio level meter

For each group (e.g., Group 1):
- `switch.group_1_active` - Combine/uncombine zones in group

### Example Automations

**Mute all zones at night:**
```yaml
automation:
  - alias: "Mute zones at night"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id:
            - switch.zone_1_mute
            - switch.zone_2_mute
            - switch.zone_3_mute
```

**Set zone volume:**
```yaml
service: number.set_value
target:
  entity_id: number.zone_1_gain
data:
  value: -20
```

## Protocol Details

This integration implements the AtlasIED Third Party Control Protocol:

- **TCP Port 5321**: Used for parameter modifications and subscriptions
- **UDP Port 3131**: Receives meter updates
- **JSON-RPC 2.0**: All messages use JSON-RPC 2.0 format
- **Methods Supported**:
  - `set` - Set parameter values
  - `bmp` - Bump (increment/decrement) values
  - `sub` - Subscribe to parameter updates
  - `unsub` - Unsubscribe from updates
  - `get` - Get current parameter value

### Message Examples

Set zone gain:
```json
{"jsonrpc":"2.0","method":"set","params":{"param":"ZoneGain_0","val":-20}}
```

Subscribe to source meter:
```json
{"jsonrpc":"2.0","method":"sub","params":{"param":"SourceMeter_0","fmt":"val"}}
```

## Troubleshooting

### Integration Not Showing Up

If the integration doesn't appear in the integrations list:

1. **Check Home Assistant logs** for errors:
   ```bash
   # View logs in real-time
   docker logs -f homeassistant
   # Or in Home Assistant UI: Settings > System > Logs
   ```

2. **Look for Python syntax errors:**
   - Search logs for `atlasied_azm` errors
   - Common issues: indentation, missing imports, type hints on older Python versions

3. **Verify file structure:**
   ```
   config/custom_components/atlasied_azm/
   ├── __init__.py
   ├── manifest.json
   ├── config_flow.py
   ├── const.py
   ├── azm_client.py
   ├── number.py
   ├── sensor.py
   ├── switch.py
   ├── strings.json
   └── translations/
       └── en.json
   ```

4. **Check manifest.json** is valid JSON (no trailing commas)

5. **Restart Home Assistant** after copying files:
   ```bash
   # Full restart required for custom component changes
   ha core restart
   ```

6. **Check Python version compatibility:**
   - This integration requires Python 3.11+ (for `str | None` syntax)
   - Check HA logs for type hint errors

### Connection Issues
- Ensure the AZM device is powered on and connected to your network
- Verify the IP address is correct
- Check that ports 5321 (TCP) and 3131 (UDP) are not blocked by firewalls
- The device must be reachable from your Home Assistant instance

### Entity Updates Not Working
- The integration automatically subscribes to parameters when entities are added
- Meter updates are sent via UDP and may take a moment to start appearing
- Check Home Assistant logs for any error messages

### Clearing Cached Configuration

If you need to clear cached settings from a previous configuration:

**Option 1: Remove Integration via UI (Recommended)**
1. Go to **Settings > Devices & Services**
2. Find the **AtlasIED AZM4/AZM8** integration
3. Click the three dots menu (⋮) and select **Delete**
4. Restart Home Assistant
5. Re-add the integration

**Option 2: Delete Configuration Files**
1. Stop Home Assistant
2. Delete the integration's config entry from `.storage/core.config_entries`
3. Delete entity registry entries from `.storage/core.entity_registry`
4. Delete device registry entries from `.storage/core.device_registry`
5. Optionally, clear `.storage/core.restore_state`
6. Restart Home Assistant

**Option 3: Force Reload (Quick Test)**
1. Go to **Settings > Devices & Services**
2. Click the three dots menu (⋮) on the integration
3. Select **Reload**
4. This reloads the integration code without deleting configuration

### Debugging Steps

1. **Enable debug logging** in `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.atlasied_azm: debug
   ```

2. **Restart Home Assistant** and watch logs:
   ```bash
   # Via Docker
   docker logs -f homeassistant | grep atlasied
   
   # Via Home Assistant CLI
   ha core restart
   tail -f /config/home-assistant.log | grep atlasied
   ```

3. **Check for specific errors:**
   - `ModuleNotFoundError`: Missing dependencies or file issues
   - `SyntaxError`: Python syntax problems
   - `AttributeError`: Missing methods or properties
   - `TypeError`: Type hint issues (need Python 3.10+)

4. **Test configuration flow:**
   - Try adding the integration via UI
   - Check logs immediately for config_flow errors
   - Look for connection errors to the device

5. **Verify entity creation:**
   ```bash
   # Check entity registry
   cat .storage/core.entity_registry | grep atlasied
   ```

## Development

The integration consists of:
- `azm_client.py` - TCP/UDP client implementation
- `__init__.py` - Integration setup and coordinator
- `config_flow.py` - Configuration UI
- `number.py` - Gain control entities
- `switch.py` - Mute and group control entities
- `sensor.py` - Name and meter sensor entities
- `const.py` - Constants and defaults
- `manifest.json` - Integration metadata
- `strings.json` / `translations/en.json` - UI strings

## License

This integration is provided as-is for use with AtlasIED AZM4/AZM8 devices.

## Support

For issues and feature requests, please open an issue on the GitHub repository.
