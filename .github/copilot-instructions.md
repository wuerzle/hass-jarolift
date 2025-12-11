# GitHub Copilot Instructions for hass-jarolift

## Project Overview

This is a Home Assistant custom component that enables control of Jarolift covers (motorized blinds/shutters) through Home Assistant. The integration acts as a proxy that adds KeeLoq encryption to commands sent via another remote entity (typically a Broadlink RM Pro+ or similar RF transmitter).

**Key Purpose**: Convert standard Home Assistant cover commands into encrypted KeeLoq packets that Jarolift covers understand, then transmit them via an RF remote.

## Architecture & Core Concepts

### KeeLoq Encryption
- **Critical**: Jarolift covers use proprietary KeeLoq encryption with a manufacturer key
- **Security**: This repository does NOT and will NOT contain the manufacturer key (MSB/LSB)
- Users must provide the manufacturer key in their configuration
- The encryption/decryption functions in `__init__.py` implement the KeeLoq algorithm

### Component Structure
```
custom_components/jarolift/
├── __init__.py          # Core KeeLoq encryption, services, packet building
├── cover.py             # Cover entity implementation
├── manifest.json        # Integration metadata
├── services.yaml        # Service definitions
└── translations/        # Service translations (en.json)
```

### Key Components

1. **Packet Building** (`BuildPacket` in `__init__.py`):
   - Encodes commands with Serial, Group, Button, Counter
   - Applies KeeLoq encryption
   - Returns base64-encoded packet for RF transmission

2. **Counter Management**:
   - Each serial has a rolling counter stored in filesystem (`counter_<serial>.txt`)
   - Counter increments with each command for replay attack prevention
   - Functions: `ReadCounter()`, `WriteCounter()`

3. **Cover Entity** (`cover.py`):
   - Implements standard Home Assistant CoverEntity
   - Button codes: `0x2` (down), `0x4` (stop), `0x8` (up)
   - Supports reverse mode for covers wired backwards

4. **Services**:
   - `jarolift.send_raw` - Send raw packet
   - `jarolift.send_command` - Send button command
   - `jarolift.learn` - Learn new cover
   - `jarolift.clear` - Clear learned cover

## Code Style & Conventions

### Python Style
- **Target**: Python 3 compatible with Home Assistant 2022.2+
- Use type hints where appropriate (newer code should include them)
- Follow Home Assistant's coding standards
- Use `_LOGGER` for logging (already imported from `logging`)
- Async/await for I/O operations (cover entity methods use `async`)

### Naming Conventions
- CamelCase for functions like `BuildPacket`, `ReadCounter`, `WriteCounter`
- snake_case for variables and methods
- UPPER_CASE for constants (e.g., `DOMAIN`, `CONF_*`)

### Configuration
- Hex values in configuration use string format: `'0x12345678'`
- Convert with `int(value, 16)` when needed
- Group and Serial are hex strings in config, converted to integers internally

## Important Dependencies

### Home Assistant Components
- `homeassistant.components.cover` - CoverEntity, CoverEntityFeature, CoverDeviceClass
- `homeassistant.helpers.config_validation` - Configuration validation
- `voluptuous` - Schema validation

### Python Standard Library
- `base64`, `binascii` - Packet encoding
- `threading` - Mutex for command synchronization
- `os.path` - Counter file management

### External Dependencies
- Requires a Home Assistant `remote` entity (e.g., Broadlink) to send RF commands
- No direct hardware communication - delegates to remote entity

## Development Guidelines

### Testing
- Test with actual Jarolift hardware is required for full validation
- Ensure counter files are properly created/updated
- Test repeat count and delay functionality
- Verify mutex prevents concurrent command sending

### Configuration Examples
```yaml
jarolift:
  remote_entity_id: remote.broadlink_rm_proplus_remote
  MSB: '0x12345678'  # Not the real key!
  LSB: '0x87654321'  # Not the real key!
  delay: 0  # Optional: delay between different covers

cover:
  - platform: jarolift
    covers:
      - name: 'Living Room Cover'
        group: '0x0001'
        serial: '0x116ea01'
        repeat_count: 4  # Optional, default 0
        repeat_delay: 0.2  # Optional, default 0.2
        reverse: False  # Optional, default False
```

### Common Patterns

**Sending Commands**:
- Always use mutex to prevent concurrent sends
- Respect repeat_count and repeat_delay
- Auto-increment counter unless explicitly provided

**Adding New Features**:
- Register new services in `setup()` function
- Update `services.yaml` with service definitions
- Add translations to `translations/en.json`

## Security Considerations

### Critical Rules
1. **NEVER** commit or expose the manufacturer key (MSB/LSB)
2. **NEVER** include actual manufacturer key values in code or examples
3. Counter files contain sensitive data - ensure proper file permissions
4. Use placeholder values like `0x12345678` in documentation

### Counter File Security
- Stored in Home Assistant config directory as `counter_<serial>.txt`
- Contains single integer (current counter value)
- Required for KeeLoq security - prevents replay attacks
- Ensure Home Assistant has write permissions to config directory

## Integration Type
- **Type**: Hub (coordinates multiple cover entities)
- **IoT Class**: `assumed_state` (no feedback from covers)
- **Domain**: `jarolift`
- **Version**: Follow semantic versioning in `manifest.json`

## Minimum Home Assistant Version
- **Current**: 2022.02.0
- Update `hacs.json` and `manifest.json` if changing minimum version

## Common Issues & Solutions

1. **Commands not working**: 
   - Verify remote entity is configured and working
   - Check manufacturer key is correct
   - Ensure counter file is writable

2. **Cover operates in reverse**:
   - Set `reverse: True` in cover configuration

3. **Multiple commands interfere**:
   - Increase global `delay` in jarolift config
   - Adjust `repeat_delay` per cover

## File Structure Notes
- Counter files: `config/counter_0x<serial>.txt`
- One counter file per serial number
- Auto-created on first use

## When Making Changes

### Adding New Button Commands
1. Define hex code constant in `JaroliftCover` class
2. Create method to call `async_push_button()` with new code
3. Update `CoverEntityFeature` if new HA feature needed

### Modifying Encryption
- **Extreme caution**: Changes to `encrypt()`/`decrypt()` break compatibility
- KeeLoq algorithm is standardized - modifications likely incorrect
- Test exhaustively with real hardware

### Updating HA Compatibility
- Check for deprecated Home Assistant APIs
- Update imports if component structure changes
- Test with target HA version before releasing
