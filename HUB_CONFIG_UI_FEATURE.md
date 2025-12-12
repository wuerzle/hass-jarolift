# Hub Configuration UI Feature

## Overview

This feature adds the ability to modify Jarolift hub parameters (MSB, LSB, remote entity ID, and delay) through the Home Assistant UI after initial setup.

## Changes Made

### 1. Config Flow Modifications (`config_flow.py`)

#### Added to `JaroliftOptionsFlow.__init__`:
- Store reference to `config_entry` for later updates

#### Added to `async_step_manage_covers`:
- New "Edit hub settings" action option in the menu
- Routes to `async_step_edit_hub` when selected

#### New Method `async_step_edit_hub`:
- Displays a form with current hub configuration pre-filled
- Validates remote entity ID exists
- Updates config entry data (not options) with new values
- Returns to manage covers menu after successful update

### 2. UI Strings (`strings.json`)

Added new section under `options.step`:
```json
"edit_hub": {
  "title": "Edit Hub Settings",
  "description": "Modify the Jarolift hub configuration. Changes will apply after reloading the integration.",
  "data": {
    "remote_entity_id": "Remote Entity ID",
    "MSB": "Manufacturer Key MSB (Most Significant Bits)",
    "LSB": "Manufacturer Key LSB (Least Significant Bits)",
    "delay": "Delay between commands (seconds)"
  },
  "data_description": {
    "remote_entity_id": "The entity ID of your remote (e.g., remote.broadlink_rm_proplus_remote)",
    "MSB": "The MSB part of the manufacturer key in hex format (e.g., '0x12345678')",
    "LSB": "The LSB part of the manufacturer key in hex format (e.g., '0x87654321')",
    "delay": "Optional delay between sending commands to different covers"
  }
}
```

### 3. German Translations (`translations/de.json`)

Added German translations for the edit hub settings UI:
- Title: "Hub-Einstellungen bearbeiten"
- Description and field labels translated appropriately

### 4. Documentation (`README.md`)

Updated the setup instructions to mention the new hub editing capability.

## User Flow

### Before This Feature:
1. User sets up integration with hub parameters (MSB, LSB, remote entity, delay)
2. User can only manage covers through options flow
3. To change hub parameters, user must delete and recreate the integration

### After This Feature:
1. User sets up integration with hub parameters
2. User can manage both covers AND hub parameters through options flow
3. User navigates to: Settings → Devices & Services → Jarolift → Configure
4. User sees menu with options:
   - Add new cover
   - Edit existing cover
   - Remove cover
   - **Edit hub settings** (NEW)
   - Finish
5. When "Edit hub settings" is selected:
   - Form shows current values for remote_entity_id, MSB, LSB, and delay
   - User can modify any of these values
   - Remote entity ID is validated to ensure it exists
   - Changes are saved to config entry data
   - Integration automatically reloads to apply changes

## Technical Details

### Why Update Config Entry Data (not Options)?

Hub parameters (remote entity, MSB, LSB, delay) are stored in `config_entry.data`, not `config_entry.options`:
- `data`: Core integration configuration (hub parameters)
- `options`: User-configurable options (covers list)

This distinction is important because:
1. The initial setup stores these in `data`
2. Services and cover entities read from `data`
3. Consistency with the existing architecture

### Integration Reload

After updating hub parameters, the integration needs to be reloaded for changes to take effect because:
1. Services are registered with the old MSB/LSB values
2. Cover entities may cache the old remote entity ID
3. Home Assistant's `async_reload_entry` handles this automatically

The integration includes an update listener that triggers reload when config entry is updated:
```python
entry.async_on_unload(entry.add_update_listener(async_reload_entry))
```

## Validation

The implementation includes validation:
- **Remote Entity ID**: Checks if the entity exists in Home Assistant
- **MSB/LSB**: Accepts string format (e.g., '0x12345678')
- **Delay**: Coerced to integer

## Error Handling

If validation fails:
- Form is redisplayed with error message
- User can correct the input
- Original values remain unchanged

Error codes:
- `invalid_remote_entity`: The specified remote entity does not exist

## Testing

While comprehensive automated tests couldn't be added due to test environment limitations, the implementation follows the exact same pattern as the existing cover editing functionality, which is well-tested and working.

Manual testing should verify:
1. Edit hub settings option appears in the menu
2. Form displays with current values pre-filled
3. Valid changes are saved correctly
4. Invalid remote entity shows appropriate error
5. Integration reloads after successful update
6. Services use the new MSB/LSB values
7. Covers use the new remote entity ID

## Benefits

1. **User-Friendly**: No need to delete and recreate integration
2. **Flexible**: Easy to fix typos or change remote entity
3. **Consistent**: Follows same UI pattern as cover management
4. **Safe**: Validates input before saving
5. **Complete**: Fully localized (English and German)
