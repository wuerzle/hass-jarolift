# Fix for Duplicate Entities and Configuration UI Error

## Issues Fixed

### 1. Configuration UI Error (500 Internal Server Error)
**Error Message:**
```
AttributeError: property 'config_entry' of 'JaroliftOptionsFlow' object has no setter
```

**Root Cause:**
In newer versions of Home Assistant, the `OptionsFlow` base class has `config_entry` as a read-only property. The code was trying to set `self.config_entry = config_entry` in the `__init__` method, which caused an AttributeError.

**Fix:**
Removed the line `self.config_entry = config_entry` from `JaroliftOptionsFlow.__init__()`. The `config_entry` is already accessible via the base class property, so storing it separately is unnecessary.

**File Changed:** `custom_components/jarolift/config_flow.py`

---

### 2. Duplicate Entities After YAML Migration

**Symptoms:**
After migrating from YAML configuration to UI configuration, entities appeared duplicated (e.g., "Wohnzimmer1" appearing twice in the entity list).

**Root Cause:**
After completing the YAML-to-UI migration, the integration created a config entry (UI configuration). However, the YAML configuration still existed in `configuration.yaml`. On the next Home Assistant restart:

1. The `setup()` function ran and set up the integration from YAML
2. The `async_setup_entry()` function also ran for the config entry
3. The `setup_platform()` function in cover.py created entities from YAML
4. The `async_setup_entry()` function in cover.py created entities from the config entry
5. Result: Each cover appeared twice!

**Fix:**
Added checks to skip YAML setup if a config entry already exists:

1. **In `__init__.py`:** Added check at the start of `setup()` to detect if a config entry exists. If yes, logs a message and returns early without setting up from YAML.

2. **In `cover.py`:** Added check at the start of `setup_platform()` to detect if a config entry exists. If yes, logs a message and returns early without creating entities.

**Files Changed:**
- `custom_components/jarolift/__init__.py`
- `custom_components/jarolift/cover.py`

---

## How to Verify the Fix

### Test 1: Configuration UI Should Open
1. Go to Settings → Devices & Services → Jarolift
2. Click the "Configure" button (gear icon)
3. The configuration UI should open without any 500 error

### Test 2: No Duplicate Entities After Migration
1. If you already have duplicate entities, you need to clean them up first:
   - Go to Settings → Devices & Services → Entities
   - Search for your Jarolift covers
   - Delete the duplicate entities (keep only one set)
   
2. Remove the YAML configuration from `configuration.yaml`:
   ```yaml
   # Remove this section:
   jarolift:
     remote_entity_id: remote.your_remote
     MSB: '0x...'
     LSB: '0x...'
   
   # And this section:
   cover:
     - platform: jarolift
       covers:
         - name: ...
   ```

3. Restart Home Assistant

4. Check that entities appear only once (no duplicates)

### Test 3: Cover Management
1. Go to Settings → Devices & Services → Jarolift → Configure
2. Try adding a new cover
3. Try editing an existing cover
4. Try removing a cover
5. All operations should work without errors

---

## Log Messages

After the fix, you will see helpful log messages:

**If YAML configuration is still present after migration:**
```
Jarolift is already configured via UI. YAML configuration is ignored. Please remove jarolift from configuration.yaml.
```

**If cover platform is called with YAML config after migration:**
```
Jarolift covers are managed via UI. YAML cover configuration is ignored.
```

These messages guide you to clean up your `configuration.yaml` file.

---

## Migration Path

### If You're Still Using Pure YAML
No changes needed! The integration still supports pure YAML configuration if no config entry exists.

### If You've Migrated to UI
1. Update to this fixed version
2. Remove the old YAML configuration from `configuration.yaml`
3. Restart Home Assistant
4. Verify entities appear only once
5. Use the UI to manage covers going forward

### If You Have Duplicate Entities
1. Update to this fixed version
2. Remove duplicate entities manually via the UI
3. Remove YAML configuration from `configuration.yaml`
4. Restart Home Assistant
5. Verify entities appear correctly

---

## Technical Details

### Code Changes Summary

**config_flow.py:**
```python
# Before (causes error):
def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
    self.config_entry = config_entry  # ❌ Error!
    self.covers = dict(config_entry.options).get(CONF_COVERS, [])

# After (fixed):
def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
    self.covers = dict(config_entry.options).get(CONF_COVERS, [])  # ✅ OK!
```

**__init__.py:**
```python
def setup(hass, config):
    if DOMAIN not in config:
        return True
    
    # NEW: Check if already configured via UI
    if hass.config_entries.async_entries(DOMAIN):
        _LOGGER.info(
            "Jarolift is already configured via UI. YAML configuration is ignored. "
            "Please remove jarolift from configuration.yaml."
        )
        return True
    
    # ... rest of YAML setup code
```

**cover.py:**
```python
def setup_platform(hass, config, add_devices, discovery_info=None):
    # NEW: Check if already configured via UI
    if hass.config_entries.async_entries(DOMAIN):
        _LOGGER.info(
            "Jarolift covers are managed via UI. YAML cover configuration is ignored."
        )
        return
    
    # ... rest of platform setup code
```

---

## Testing

New tests were added in `tests/test_duplicate_prevention.py` to verify:
- YAML setup is skipped when a config entry exists
- Cover platform setup is skipped when a config entry exists

Existing tests still pass:
- All standalone tests (encryption, packet building, counters) pass
- Config flow tests work correctly

---

## Compatibility

- **Home Assistant:** 2022.2.0 and newer
- **Breaking Changes:** None
- **Migration:** Automatic (just update and remove YAML config)
