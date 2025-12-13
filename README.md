# Jarolift Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Control your Jarolift covers (motorized blinds/shutters) through Home Assistant. This custom component acts as a proxy that adds KeeLoq encryption to commands sent via a Home Assistant 'remote' entity (typically a Broadlink RM Pro+ or similar RF transmitter).

## Features

- **UI Configuration**: Configure via Home Assistant UI (Settings → Devices & Services)
- **YAML Support**: Legacy YAML configuration with automatic migration to UI
- **Multiple Covers**: Control individual covers or groups of covers
- **KeeLoq Security**: Built-in KeeLoq encryption for secure communication
- **Repeat Transmission**: Configurable repeat count for improved RF reliability
- **Learning Mode**: Learn new covers directly through Home Assistant services

## Credits

The code originates from [this Home Assistant Community discussion](https://community.home-assistant.io/t/control-of-jarolift-covers-using-broadlink-rm-pro/35600). This repository maintains and updates the integration for compatibility with newer Home Assistant versions.

## Supported Home Assistant versions

### Minimum HA version: 2022.2
Older versions may be supported by tagged versions (see tags).

## KeeLoq Encryption

Jarolift covers use [KeeLoq](https://en.wikipedia.org/wiki/KeeLoq) encryption hence there is always a
proprietary bit of knowledge needed to operate them (the manufacturer key which is used in the process
of encrypting/decrypting data).

**This repository does not and will not contain the secret manufacturer key!**

If you do not have the manufacturer key you should get it by using Google or follow the linked original source from above ;-)

## Installation

Make sure you have the manufacturer secret (MSB and LSB from it are required).
Also you need to have a remote configured that is able to send data (via RF) to your Jarolift covers.
This could for example be an Broadlink RM PRO+ with the appropriate [Home Assistant Integration](https://www.home-assistant.io/integrations/broadlink/)
configured.

### Installation via HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Click the button below to open this integration in HACS:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=wuerzle&repository=hass-jarolift&category=integration)

3. Alternatively, search for "Jarolift" in HACS and install it
4. Restart Home Assistant
5. Continue with the [Setup](#setup) section below

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/wuerzle/hass-jarolift/releases)
2. Copy the `custom_components/jarolift` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant
4. Continue with the [Setup](#setup) section below

### Setup

**Note:** Starting with version 2.0.0, the integration supports configuration via the Home Assistant UI. YAML configuration is still supported for backward compatibility and will be automatically migrated to UI configuration.

#### Setup via UI (Recommended)

1. Go to **Settings** → **Devices & Services** in Home Assistant
2. Click **+ ADD INTEGRATION**
3. Search for "Jarolift" and select it
4. Enter the following information:
   - **Remote Entity ID**: The entity ID of your RF remote (e.g., `remote.broadlink_rm_proplus_remote`)
   - **Manufacturer Key MSB**: Most significant bits of the manufacturer key in hex format (e.g., `0x12345678`)
   - **Manufacturer Key LSB**: Least significant bits of the manufacturer key in hex format (e.g., `0x87654321`)
   - **Delay** (optional): Delay in seconds between sending commands to different covers (default: 0)
5. Click **Submit**
6. The integration is now configured. To add covers, click **Configure** on the Jarolift integration card
7. Select "Add new cover" and enter:
   - **Name**: Friendly name for the cover (e.g., "Living Room Cover")
   - **Group**: Group ID in hex format (e.g., `0x0001`)
   - **Serial**: Serial number in hex format (e.g., `0x106aa01`)
   - **Repeat Count** (optional): Number of times to repeat transmission (default: 0)
   - **Repeat Delay** (optional): Delay between repeated transmissions in seconds (default: 0.2)
   - **Reverse Up/Down** (optional): Check this if your cover closes on "up" and opens on "down"
8. Repeat step 7 for each cover you want to add

**Note:** You can also edit existing covers, remove covers, or modify hub settings (remote entity, MSB, LSB, delay) at any time by clicking **Configure** on the Jarolift integration card and selecting "Edit hub settings" or the appropriate cover action.

#### Setup via YAML (Legacy - Will be migrated automatically)

If you have an existing YAML configuration, it will be automatically imported to UI configuration on the next Home Assistant restart.

Enter following lines to `configuration.yaml`

```yaml
jarolift:
  remote_entity_id: remote.broadlink_rm_proplus_remote # this id is from the device of the remote integration representing the remote to send command with
  MSB: '0x12345678' # Most significant bits of the manufacturer key (**0x12345678 is not the correct value!**)
  LSB: '0x87654321' # Least significant bits of the manufactorer key (**0x87654321 is not the correct value!**)
```
Manufacturer key can be found on pastebin (just google it)

You can then use the new cover platform like this:
```yaml
cover:
  - platform: jarolift
  covers:
    - name: 'Livingroom Main Cover'
      group: '0x0001'
      serial: '0x116ea01'
      # The following two are optional
      repeat_count: 4	# number of times a command is sent - default = 0
      repeat_delay: 0.2 # delay in seconds between multiple transmissions - default = 0.2
      reverse: False # Do reverse up and down commands. Useful if your cover closes on sending "up" and opens on sending "down".
```

Make sure Home Assistant can write files in the config directory. The integration will write one to keep
track of the current count of command sent per serial. This count is required for the KeeLoq encryption.

**After YAML import:** Once your configuration has been imported to UI configuration, you can safely remove the Jarolift configuration from your `configuration.yaml` file. The integration will continue to work with the UI-based configuration. All future cover management should be done through the UI (Settings → Devices & Services → Jarolift → Configure).

Save the configuration file and restart Home Assistant.

## Provided services
The integration provides following services:
* jarolift.clear
* jarolift.learn
* jarolift.send_command
* jarolift.send_raw

Those are documented in the [services.yaml](https://github.com/wuerzle/hass-jarolift/blob/main/custom_components/jarolift/services.yaml).

## Learn covers

Use the provided services from your Home Assistant Developers Tools view to connect to your covers. Use the process that is normally executed when
learning an original Jarolift remote.

## Understanding Groups and Controlling Multiple Covers

### How Groups Work

Groups in Jarolift use bit flags to determine which covers respond to a command. Each cover can be configured with one or more group bits:

- `0x0001` - Group 1 (bit 0)
- `0x0002` - Group 2 (bit 1)
- `0x0004` - Group 3 (bit 2)
- `0x0008` - Group 4 (bit 3)
- etc.

### Controlling All Covers

To control multiple covers simultaneously, you have two options:

#### Option 1: Use Combined Group Bits (Recommended)

Use the bitwise OR of all individual group values. For example, if you have covers with groups `0x0001`, `0x0002`, `0x0004`, and `0x0008`, use:

```yaml
- name: 'All Covers'
  group: '0x000F'  # 0x0001 | 0x0002 | 0x0004 | 0x0008 = 0x000F
  serial: '0x106aa01'  # Use any valid serial, typically same as one of your covers
```

#### Option 2: Use Broadcast Group (Not Always Supported)

Some Jarolift covers may respond to `0xFFFF` as a broadcast group, but this is not guaranteed:

```yaml
- name: 'All Covers'
  group: '0xFFFF'  # Broadcast to all groups
  serial: '0x106aa01'  # Use any valid serial
```

### Important Notes

1. **Serial Number**: When controlling multiple covers, use the serial number of one of your existing covers. The serial determines which counter file is used for KeeLoq encryption.

2. **Learning Required**: Each cover must be learned with its specific group value. Covers only respond to commands that match their learned group bits.

3. **Counter Synchronization**: All covers sharing the same serial number share the same counter file. If you use `repeat_count > 0`, make sure the value is appropriate for RF reliability in your environment.

4. **Example Configuration**:
   ```yaml
   cover:
     - platform: jarolift
       covers:
         - name: 'Living Room Left'
           group: '0x0001'
           serial: '0x106aa01'
           repeat_count: 4
         - name: 'Living Room Right'
           group: '0x0002'
           serial: '0x106aa02'
           repeat_count: 4
         - name: 'Both Living Room Covers'
           group: '0x0003'  # 0x0001 | 0x0002
           serial: '0x106aa01'
           repeat_count: 4
   ```

## Troubleshooting

### Counter Issues with repeat_count

If you experience issues where you need to press buttons multiple times before covers respond (especially after using `repeat_count > 0`), this was a known bug that has been fixed. Make sure you're using the latest version of the integration.

The fix ensures that when `repeat_count > 0`, each transmission uses a unique, incrementing counter value, maintaining proper KeeLoq security and preventing desynchronization.
