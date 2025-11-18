# AtlasIED AZM8 Home Assistant Integration# AtlasIED AZM8 Home Assistant Integration



A custom Home Assistant integration for the **AtlasIED AZM8** 8-Zone Audio Mixer, providing complete control over all 8 audio zones through the Home Assistant interface using the official JSON-RPC 2.0 protocol.A custom Home Assistant integration for the **AtlasIED AZM8** 8-Zone Audio Mixer, providing complete control over all 8 audio zones through the Home Assistant interface.



## Features## Features



- 🎵 **8 Independent Zone Control**: Control all 8 zones as separate media player entities- 🎵 **8 Independent Zone Control**: Control all 8 zones as separate media player entities

- 🔊 **Volume Control**: Adjust volume levels (0-100%) for each zone- 🔊 **Volume Control**: Adjust volume levels (0-100%) for each zone

- 🔇 **Mute Control**: Mute/unmute individual zones- 🔇 **Mute Control**: Mute/unmute individual zones

- 🎚️ **Source Selection**: Switch between 8 input sources per zone- ⚡ **Power Control**: Turn zones on/off independently

- 🔄 **Automatic Updates**: Real-time status updates via polling- 🎚️ **Source Selection**: Switch between 8 input sources per zone

- 🖥️ **UI Configuration**: Easy setup through Home Assistant UI- 🔄 **Automatic Updates**: Real-time status updates via polling

- 🔌 **Native Protocol**: Uses official JSON-RPC 2.0 over TCP- 🖥️ **UI Configuration**: Easy setup through Home Assistant UI



## Installation## Installation



### HACS (Recommended)### HACS (Recommended)



1. Open HACS in Home Assistant1. Open HACS in Home Assistant

2. Go to "Integrations"2. Go to "Integrations"

3. Click the three dots in the top right corner3. Click the three dots in the top right corner

4. Select "Custom repositories"4. Select "Custom repositories"

5. Add this repository URL: `https://github.com/NorthTrailRV/AtlasIEDIntegration`5. Add this repository URL and select "Integration" as the category

6. Select "Integration" as the category6. Click "Install"

7. Click "Install"7. Restart Home Assistant

8. Restart Home Assistant

### Manual Installation

### Manual Installation

1. Copy the `custom_components/atlasied_azm8` folder to your Home Assistant's `custom_components` directory

1. Copy the `custom_components/atlasied_azm8` folder to your Home Assistant's `custom_components` directory2. If the `custom_components` directory doesn't exist, create it in the same location as your `configuration.yaml`

2. If the `custom_components` directory doesn't exist, create it in the same location as your `configuration.yaml`3. Restart Home Assistant

3. Restart Home Assistant

## Configuration

## Configuration

### Through the UI (Recommended)

### Through the UI (Recommended)

1. Navigate to **Settings** → **Devices & Services**

1. Navigate to **Settings** → **Devices & Services**2. Click **+ Add Integration**

2. Click **+ Add Integration**3. Search for "AtlasIED AZM8"

3. Search for "AtlasIED AZM8"4. Enter your device configuration:

4. Enter your device configuration:   - **Host**: IP address or hostname of your AZM8 device

   - **Host**: IP address or hostname of your AZM8 device   - **Name**: Friendly name for your device (default: "AtlasIED AZM8")

   - **Name**: Friendly name for your device (default: "AtlasIED AZM8")5. Click **Submit**

5. Click **Submit**

**Note**: The integration automatically uses TCP port 5321, which is the standard control port for the AZM8.

**Note**: The integration automatically uses TCP port 5321, which is the standard control port for the AZM8.

The integration will create 8 media player entities, one for each zone:

The integration will create 8 media player entities, one for each zone:- `media_player.atlasied_azm8_zone_1`

- `media_player.atlasied_azm8_zone_1`- `media_player.atlasied_azm8_zone_2`

- `media_player.atlasied_azm8_zone_2`- ... through Zone 8

- ... through Zone 8

## Usage

## Usage

### Control Zones

### Control Zones

Each zone can be controlled independently through:

Each zone can be controlled independently through:

**Volume Control:**

**Volume Control:**```yaml

```yamlservice: media_player.volume_set

service: media_player.volume_settarget:

target:  entity_id: media_player.atlasied_azm8_zone_1

  entity_id: media_player.atlasied_azm8_zone_1data:

data:  volume_level: 0.5  # 50% volume

  volume_level: 0.5  # 50% volume```

```

**Mute/Unmute:**

**Mute/Unmute:**```yaml

```yamlservice: media_player.volume_mute

service: media_player.volume_mutetarget:

target:  entity_id: media_player.atlasied_azm8_zone_1

  entity_id: media_player.atlasied_azm8_zone_1data:

data:  is_volume_muted: true

  is_volume_muted: true```

```

**Power Control:**

**Turn On/Off:**```yaml

```yamlservice: media_player.turn_on

service: media_player.turn_ontarget:

target:  entity_id: media_player.atlasied_azm8_zone_1

  entity_id: media_player.atlasied_azm8_zone_1```

```

**Source Selection:**

**Source Selection:**```yaml

```yamlservice: media_player.select_source

service: media_player.select_sourcetarget:

target:  entity_id: media_player.atlasied_azm8_zone_1

  entity_id: media_player.atlasied_azm8_zone_1data:

data:  source: "Input 3"

  source: "Source 3"```

```

### Automations Example

### Automations Example

```yaml

```yamlautomation:

automation:  - alias: "Morning Music in All Zones"

  - alias: "Morning Music in All Zones"    trigger:

    trigger:      - platform: time

      - platform: time        at: "07:00:00"

        at: "07:00:00"    action:

    action:      - service: media_player.turn_on

      - service: media_player.turn_on        target:

        target:          entity_id:

          entity_id:            - media_player.atlasied_azm8_zone_1

            - media_player.atlasied_azm8_zone_1            - media_player.atlasied_azm8_zone_2

            - media_player.atlasied_azm8_zone_2      - service: media_player.select_source

      - service: media_player.select_source        target:

        target:          entity_id:

          entity_id:            - media_player.atlasied_azm8_zone_1

            - media_player.atlasied_azm8_zone_1            - media_player.atlasied_azm8_zone_2

            - media_player.atlasied_azm8_zone_2        data:

        data:          source: "Input 1"

          source: "Source 0"      - service: media_player.volume_set

      - service: media_player.volume_set        target:

        target:          entity_id:

          entity_id:            - media_player.atlasied_azm8_zone_1

            - media_player.atlasied_azm8_zone_1            - media_player.atlasied_azm8_zone_2

            - media_player.atlasied_azm8_zone_2        data:

        data:          volume_level: 0.3

          volume_level: 0.3```

```

## Device Configuration

## Device Configuration

### API Protocol

### API Protocol

This integration communicates with the AtlasIED AZM8 using **JSON-RPC 2.0** over **TCP port 5321**. Ensure that:

This integration communicates with the AtlasIED AZM8 using **JSON-RPC 2.0** over **TCP port 5321**. Ensure that:- Your AZM8 device is connected to your network

- Your AZM8 device is connected to your network- The device's IP address is accessible from Home Assistant

- The device's IP address is accessible from Home Assistant- TCP port 5321 is accessible (default control port for AZM8/AZM4)

- TCP port 5321 is accessible (default control port for AZM8/AZM4)- Any firewalls allow communication on port 5321

- Any firewalls allow communication on port 5321

### Technical Details

### Technical Details

- **Protocol**: JSON-RPC 2.0

- **Protocol**: JSON-RPC 2.0- **Transport**: TCP

- **Transport**: TCP- **Port**: 5321 (control), 3131 (UDP for meter updates)

- **Port**: 5321 (control), 3131 (UDP for meter updates)- **Message Format**: Newline-delimited JSON messages

- **Message Format**: Newline-delimited JSON messages- **Volume Range**: -80 dB to +10 dB (mapped to 0-100% in UI)

- **Volume Range**: -80 dB to +10 dB (mapped to 0-100% in UI)- **Zone Indexing**: 0-based (Zone 1 = index 0)

- **Zone Indexing**: 0-based (Zone 1 = index 0)

## Supported Features

## Supported Features

- ✅ Volume control (0-100%)

- ✅ Volume control (0-100%)- ✅ Mute control

- ✅ Mute control- ✅ Power on/off

- ✅ Turn on/off zones- ✅ Source selection (8 inputs)

- ✅ Source selection (8 inputs)- ✅ Independent zone control

- ✅ Independent zone control- ✅ Status polling

- ✅ Status polling

## Troubleshooting

## Troubleshooting

### Connection Issues

### Connection Issues

If you cannot connect to the device:

If you cannot connect to the device:1. Verify the IP address and port are correct

1. Verify the IP address is correct2. Check that the AZM8 is powered on and connected to the network

2. Check that the AZM8 is powered on and connected to the network3. Ensure there are no firewall rules blocking communication

3. Ensure TCP port 5321 is accessible (test with `telnet <ip> 5321`)4. Check Home Assistant logs for detailed error messages

4. Check Home Assistant logs for detailed error messages

5. Run the included test script: `./test_volume_query.sh <ip_address>`### Viewing Logs



### Viewing LogsEnable debug logging by adding this to your `configuration.yaml`:



Enable debug logging by adding this to your `configuration.yaml`:```yaml

logger:

```yaml  default: info

logger:  logs:

  default: info    custom_components.atlasied_azm8: debug

  logs:```

    custom_components.atlasied_azm8: debug

```## Contributing



## TestingContributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.



A test script is included to verify communication with the AZM8:## License



```bashThis project is licensed under the MIT License.

./test_volume_query.sh 192.168.10.50

```## Support



This will query all zones and display their current status.For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/berapp/atlasied_azm8).



## Contributing## Credits



Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.Developed for the Home Assistant community to provide seamless integration with AtlasIED AZM8 audio equipment.


## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/NorthTrailRV/AtlasIEDIntegration).

## Credits

Developed for the Home Assistant community to provide seamless integration with AtlasIED AZM8 audio equipment using the official JSON-RPC 2.0 protocol.
