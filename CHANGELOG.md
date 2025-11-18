# Changelog

## [Unreleased] - 2025-11-18

### Changed
- **BREAKING**: Updated to use correct AtlasIED AZM8 API protocol
  - Changed from HTTP to TCP/JSON-RPC 2.0
  - Updated default port from 80 to 5321
  - Removed aiohttp dependency (using native asyncio)

### Updated Files
- `const.py`: Changed DEFAULT_PORT to 5321, added NUM_ZONES constant
- `coordinator.py`: Complete rewrite to use TCP/JSON-RPC 2.0 protocol
  - Implemented persistent TCP connection with auto-reconnect
  - Added proper JSON-RPC message formatting
  - Changed from HTTP endpoints to parameter-based commands
  - Volume now uses dB scale (-80 to +10 dB)
  - Zone indexing changed to 0-based (Zone 1 = index 0)
- `media_player.py`: Updated to work with new coordinator
  - Changed volume mapping from 0-100 to dB scale conversion
  - Updated zone indexing to 0-based
  - Changed source selection to use numeric indices
  - Removed power control (zones use mute instead)
- `__init__.py`: Added coordinator shutdown on unload
- `manifest.json`: Removed aiohttp requirement
- `README.md`: Updated with correct protocol documentation

### Technical Details

#### Protocol Specification
- **Transport**: TCP on port 5321
- **Format**: JSON-RPC 2.0 with newline delimiters
- **Message Examples**:
  ```json
  {"jsonrpc":"2.0","method":"get","params":{"param":"ZoneGain_0","fmt":"val"}}
  {"jsonrpc":"2.0","method":"set","params":{"param":"ZoneGain_0","val":-10}}
  {"jsonrpc":"2.0","method":"set","params":{"param":"ZoneMute_0","val":1}}
  ```

#### Parameter Naming
- Zone parameters use 0-based indexing: `ZoneGain_0` through `ZoneGain_7`
- Available parameters per zone:
  - `ZoneGain_N`: Volume in dB (-80 to +10)
  - `ZoneMute_N`: Mute state (0=unmuted, 1=muted)
  - `ZoneSource_N`: Source index (0-7)
  - `ZoneName_N`: Zone name (read-only)

#### Volume Mapping
- AZM8 native: -80 dB (silent) to +10 dB (max)
- Home Assistant: 0.0 (silent) to 1.0 (max)
- Conversion: `volume = (gain_dB + 80) / 90`

### Testing
Added `test_volume_query.sh` script to verify TCP/JSON-RPC communication with the AZM8 device.
