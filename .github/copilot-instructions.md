# GitHub Copilot Instructions for hass-jarolift

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture & Core Concepts](#architecture--core-concepts)
- [Development Environment Setup](#development-environment-setup)
- [Build, Test, and Lint Commands](#build-test-and-lint-commands)
- [CI/CD Pipeline](#cicd-pipeline)
- [Code Style & Conventions](#code-style--conventions)
- [Important Dependencies](#important-dependencies)
- [Development Guidelines](#development-guidelines)
- [Critical Files - Handle With Care](#critical-files---handle-with-care)
- [Common Pitfalls and How to Avoid Them](#common-pitfalls-and-how-to-avoid-them)
- [Security Considerations](#security-considerations)
- [Integration Type](#integration-type)
- [Version Management](#version-management)
- [Common Issues & Solutions](#common-issues--solutions)
- [Debugging and Troubleshooting](#debugging-and-troubleshooting)
- [Quick Reference](#quick-reference)
- [Summary](#summary)

## Project Overview

This is a Home Assistant custom component that enables control of Jarolift covers (motorized blinds/shutters) through Home Assistant. The integration acts as a proxy that adds KeeLoq encryption to commands sent via another remote entity (typically a Broadlink RM Pro+ or similar RF transmitter).

**Key Purpose**: Convert standard Home Assistant cover commands into encrypted KeeLoq packets that Jarolift covers understand, then transmit them via an RF remote.

**Installation**: Available via HACS (Home Assistant Community Store) or manual installation. See README.md for details.

**Current Version**: 2.0.0+ (supports UI configuration with automatic YAML migration)

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
├── config_flow.py       # Configuration flow for UI-based setup
├── cover.py             # Cover entity implementation
├── manifest.json        # Integration metadata
├── services.yaml        # Service definitions
├── strings.json         # English UI translations
└── translations/        # Service and UI translations (en.json, de.json)
    ├── en.json          # English translations
    └── de.json          # German translations

tests/
├── __init__.py          # Test package marker
├── conftest.py          # Pytest fixtures and configuration
├── test_standalone.py   # Standalone tests (no HA required)
├── test_config_flow.py  # Config flow tests
├── test_init.py         # Integration tests
├── test_core_functions.py # Additional core function tests
└── README.md            # Test documentation

Configuration Files:
├── pyproject.toml       # Pytest configuration
├── ruff.toml            # Ruff linter/formatter configuration
├── requirements_test.txt # Test dependencies
└── hacs.json            # HACS integration metadata
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

4. **Configuration Flow** (`config_flow.py`):
   - UI-based configuration (recommended, added in v2.0.0)
   - Automatic YAML import and migration
   - Options flow for managing covers (add/edit/remove)
   - Validates entity IDs, hex values, and duplicate detection
   - Supports both ConfigEntry and legacy YAML setup

5. **Services**:
   - `jarolift.send_raw` - Send raw packet
   - `jarolift.send_command` - Send button command
   - `jarolift.learn` - Learn new cover
   - `jarolift.clear` - Clear learned cover

## Code Style & Conventions

### Python Style
- **Target**: Python 3.11+ compatible with Home Assistant 2022.2+
- **Linter/Formatter**: Ruff (configured in `ruff.toml`)
- **Line Length**: 88 characters (same as Black)
- **Quotes**: Double quotes for strings
- **Import Sorting**: Handled by Ruff (isort rules)
- Use type hints where appropriate (newer code should include them)
- Follow Home Assistant's coding standards
- Use `_LOGGER` for logging (already imported from `logging`)
- Async/await for I/O operations (cover entity methods use `async`)
- **Never use print()** - always use `_LOGGER.debug()`, `_LOGGER.info()`, `_LOGGER.warning()`, or `_LOGGER.error()`

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

## Development Environment Setup

### Prerequisites
- Python 3.11 or higher
- Home Assistant 2022.2.0 or higher
- Git for version control

### Initial Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/wuerzle/hass-jarolift.git
   cd hass-jarolift
   ```

2. Install development dependencies:
   ```bash
   pip install homeassistant>=2022.2.0
   pip install ruff
   pip install -r requirements_test.txt
   ```

3. Verify setup:
   ```bash
   python tests/test_standalone.py
   ```

### Development Workflow
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes to the code
3. Run linter and formatter: `ruff check custom_components/` and `ruff format custom_components/`
4. Run tests: `pytest tests/` or `python tests/test_standalone.py`
5. Commit changes with descriptive messages
6. Push and create a pull request

## Build, Test, and Lint Commands

### Linting and Formatting
**Run Ruff linter:**
```bash
ruff check custom_components/
```

**Run Ruff formatter:**
```bash
ruff format custom_components/
```

**Check formatting without changes:**
```bash
ruff format --check custom_components/
```

### Testing
**Run standalone tests (no Home Assistant required):**
```bash
python tests/test_standalone.py
```

**Run full test suite:**
```bash
pytest tests/
```

**Run with verbose output:**
```bash
pytest tests/ -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=custom_components.jarolift --cov-report=html
```

**Run specific test file:**
```bash
pytest tests/test_standalone.py -v
pytest tests/test_config_flow.py -v
pytest tests/test_init.py -v
```

### Validation Commands
**Validate Python syntax:**
```bash
python -m py_compile custom_components/jarolift/__init__.py
python -m py_compile custom_components/jarolift/cover.py
python -m py_compile custom_components/jarolift/config_flow.py
```

**Validate manifest.json:**
```bash
python -c "import json; json.load(open('custom_components/jarolift/manifest.json'))"
```

**Validate services.yaml:**
```bash
pip install pyyaml
python -c "import yaml; yaml.safe_load(open('custom_components/jarolift/services.yaml'))"
```

**Check for print statements (should use _LOGGER):**
```bash
grep -r "print(" custom_components/jarolift/*.py
```

## CI/CD Pipeline

### GitHub Actions Workflows
The repository uses GitHub Actions for continuous integration with the following workflow:

**Quality Review Workflow** (`.github/workflows/quality-review.yml`):
- **Triggers**: On push to `main` or pull requests to `main`
- **Jobs**:
  1. **Quality Review**:
     - Runs on Ubuntu with Python 3.11
     - Installs Home Assistant and Ruff
     - Runs linter and formatter checks (currently informational)
     - Validates Python syntax
     - Validates manifest.json and services.yaml
     - Checks for print statements
  2. **HACS Validation**:
     - Validates integration for HACS compatibility
     - Ensures proper integration structure

### Pre-commit Checklist
Before pushing code, ensure:
- [ ] Code passes Ruff linting: `ruff check custom_components/`
- [ ] Code is properly formatted: `ruff format custom_components/`
- [ ] All tests pass: `pytest tests/` or `python tests/test_standalone.py`
- [ ] Python syntax is valid
- [ ] No print() statements (use `_LOGGER` instead)
- [ ] manifest.json and services.yaml are valid
- [ ] Counter files are properly tested if changes affect counter logic

## Development Guidelines

### Testing
- **Standalone tests** (`test_standalone.py`): Test core functions without Home Assistant
- **Integration tests** (`test_config_flow.py`, `test_init.py`): Test with Home Assistant
- Test with actual Jarolift hardware is required for full validation
- Ensure counter files are properly created/updated
- Test repeat count and delay functionality
- Verify mutex prevents concurrent command sending
- Run `python tests/test_standalone.py` for quick validation during development

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
- Register new services in `async_setup_entry()` or `setup()` function
- Update `services.yaml` with service definitions
- Add translations to `translations/en.json` and `translations/de.json`
- Add corresponding entries in `strings.json` for UI elements
- Test with both ConfigEntry and legacy YAML setup modes

**Configuration Flow Changes**:
- Update schemas in `config_flow.py`
- Add validation in config flow methods
- Update UI strings in `strings.json`
- Test the complete flow: initial setup → options → add/edit/remove covers

## Critical Files - Handle With Care

### DO NOT Modify Without Deep Understanding
1. **KeeLoq Encryption Functions** (`__init__.py`):
   - `encrypt()` and `decrypt()` - Changes break compatibility with Jarolift covers
   - `bitRead()` and `bitSet()` - Core bit manipulation functions
   - These implement the standardized KeeLoq algorithm

2. **Packet Building** (`BuildPacket()` in `__init__.py`):
   - Changes can make covers non-responsive
   - Test exhaustively with real hardware if modified

3. **Counter Management** (`ReadCounter()`, `WriteCounter()` in `__init__.py`):
   - Critical for security (prevents replay attacks)
   - Counter files must be properly managed

### Files That Should Rarely Change
- `manifest.json` - Only for version bumps or dependency changes
- `services.yaml` - Only when adding/modifying services
- `hacs.json` - Only for HACS configuration changes

### Safe to Modify (With Testing)
- `cover.py` - Cover entity implementation
- `config_flow.py` - Configuration UI flow
- Translation files (`strings.json`, `translations/*.json`)
- `README.md` - Documentation
- Test files (`tests/*.py`)

## Common Pitfalls and How to Avoid Them

### 1. Breaking KeeLoq Encryption
**Problem**: Modifying encryption functions breaks communication with covers
**Solution**: Never modify `encrypt()`, `decrypt()`, `bitRead()`, or `bitSet()` unless you fully understand KeeLoq

### 2. Counter File Race Conditions
**Problem**: Multiple simultaneous commands can corrupt counter files
**Solution**: Always use the `mutex` lock when sending commands

### 3. Duplicate Service Registration
**Problem**: Services registered multiple times cause errors
**Solution**: Use `_register_services()` helper and check `hass.data` before registering

### 4. YAML Import Timing
**Problem**: Importing YAML before covers are registered loses cover data
**Solution**: Use delayed import with `call_later()` to allow cover platform setup

### 5. Hex Value Parsing
**Problem**: Inconsistent hex value parsing across the codebase
**Solution**: Always use `_parse_hex_config_value()` helper function

### 6. Using print() Instead of Logging
**Problem**: print() statements fail in production and aren't configurable
**Solution**: Always use `_LOGGER.debug()`, `.info()`, `.warning()`, or `.error()`

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
- Test with the minimum supported version before releasing

## Version Management

### Semantic Versioning
Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes (e.g., removing YAML support)
- **MINOR**: New features (e.g., adding config flow UI)
- **PATCH**: Bug fixes and small improvements

### Where to Update Version
When releasing a new version, update in these files:
1. `custom_components/jarolift/manifest.json` - `"version"` field
2. Create a git tag: `git tag v2.0.0` (matches manifest version)
3. Consider updating README.md with version-specific notes if needed

### Release Checklist
Before releasing:
- [ ] All tests pass (`pytest tests/`)
- [ ] Linting passes (`ruff check custom_components/`)
- [ ] Formatting correct (`ruff format --check custom_components/`)
- [ ] Version bumped in `manifest.json`
- [ ] IMPLEMENTATION_SUMMARY.md updated if major changes
- [ ] README.md updated with new features/breaking changes
- [ ] Git tag created matching version
- [ ] Tested with real Jarolift hardware (if encryption/protocol changes)

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

## Debugging and Troubleshooting

### Enable Debug Logging
Add to Home Assistant's `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.jarolift: debug
```

Then restart Home Assistant and check logs at **Settings → System → Logs**

### Common Debugging Scenarios

**Issue: Integration not loading**
- Check Home Assistant logs for error messages
- Verify manifest.json is valid JSON
- Ensure all required files exist in `custom_components/jarolift/`
- Check file permissions

**Issue: Cover not responding to commands**
- Enable debug logging to see packet generation
- Verify remote entity is working (`remote.send_command` service)
- Check counter file is being written correctly
- Verify manufacturer key (MSB/LSB) is correct
- Test with `jarolift.send_command` service directly

**Issue: Counter file problems**
- Check Home Assistant config directory is writable
- Look for `counter_0x<serial>.txt` files
- Manually verify counter increments: `cat config/counter_0x*.txt`
- Counter should increment with each command sent

**Issue: Config flow not appearing**
- Verify `manifest.json` has `"config_flow": true`
- Clear browser cache
- Restart Home Assistant
- Check for errors in logs during startup

### Testing Changes

**Quick Test Cycle**:
1. Make code changes
2. Run standalone tests: `python tests/test_standalone.py`
3. Check syntax: `python -m py_compile custom_components/jarolift/*.py`
4. Run linter: `ruff check custom_components/`
5. Format code: `ruff format custom_components/`

**Full Test Cycle**:
1. Run all tests: `pytest tests/ -v`
2. Test in Home Assistant development environment
3. Verify with actual Jarolift hardware (if protocol changes)
4. Check counter files are being updated properly
5. Test both YAML and UI configuration modes

### Useful Debug Commands

**Check which covers are configured**:
```bash
grep -r "serial" ~/.homeassistant/custom_components/jarolift/ || \
grep -r "serial" /config/custom_components/jarolift/
```

**View counter files**:
```bash
ls -la ~/.homeassistant/counter_*.txt || \
ls -la /config/counter_*.txt
```

**Test packet generation** (in Python REPL):
```python
import sys
sys.path.insert(0, 'custom_components/jarolift')
from __init__ import BuildPacket

# Test packet (use test MSB/LSB, not real keys!)
packet = BuildPacket(0x12345678, 0x87654321, 0x116ea01, 0x0001, 0x8, 1)
print(packet)
```

## Quick Reference

### Most Common Tasks

**Add a new service**:
1. Define service in `services.yaml`
2. Register handler in `async_setup_entry()` or `setup()`
3. Add translations in `strings.json` and `translations/*.json`
4. Test service from Developer Tools

**Add a new configuration option**:
1. Update schema in `config_flow.py`
2. Add to `strings.json` for UI labels
3. Update cover entity to use the new option
4. Add translations

**Fix a bug**:
1. Create test that reproduces the bug
2. Fix the code
3. Verify test passes
4. Run full test suite
5. Test manually if hardware-related

**Update translations**:
1. Edit `translations/en.json` for English
2. Edit `translations/de.json` for German
3. Update `strings.json` for UI elements
4. Test in Home Assistant UI (change language to verify)

### Key Files Quick Reference

| File | Purpose | When to Modify |
|------|---------|----------------|
| `__init__.py` | Core logic, encryption, services | Add services, fix core bugs |
| `cover.py` | Cover entity implementation | Change cover behavior |
| `config_flow.py` | UI configuration | Modify configuration UI |
| `manifest.json` | Integration metadata | Version bump, dependencies |
| `services.yaml` | Service definitions | Add/modify services |
| `strings.json` | UI text (English) | UI changes |
| `translations/en.json` | Service translations (EN) | Add services, change text |
| `translations/de.json` | Service translations (DE) | Add services, change text |
| `ruff.toml` | Linter configuration | Change code style rules |
| `pyproject.toml` | Test configuration | Change test settings |

## Summary

This integration bridges Home Assistant and Jarolift covers using KeeLoq encryption. When making changes:
1. **Prioritize security** - Never expose manufacturer keys
2. **Test thoroughly** - KeeLoq changes can break devices
3. **Use proper tools** - Ruff for linting, pytest for testing
4. **Follow conventions** - Use _LOGGER, async/await, type hints
5. **Document changes** - Update README and translations
6. **Be minimal** - Don't change encryption unless absolutely necessary

The integration supports both UI (ConfigEntry) and YAML configuration, with automatic migration. Always test both modes when making significant changes.
