# Expected UI Result - Entity Listing

## Integration Page View

When users navigate to **Settings → Devices & Services** and find "Jarolift", they will see:

```
╔═══════════════════════════════════════════════════════════════╗
║                   Jarolift Integration                        ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📱 Jarolift                                                  ║
║  Integration Type: Hub                                        ║
║  IoT Class: Assumed State                                     ║
║                                                               ║
║  1 Device • 4 Entities • 4 Services                          ║
║                                                               ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          ║
║  │ Configure   │  │   Reload    │  │   Remove    │          ║
║  └─────────────┘  └─────────────┘  └─────────────┘          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

## Device Detail View

Clicking on the integration card shows the device and entities:

```
╔═══════════════════════════════════════════════════════════════╗
║  ← Back to Integrations                                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Jarolift                                                     ║
║  Jarolift Integration                                         ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  DEVICES (1)                                                  ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │  🎛️  Jarolift                                     ⚙️ ⋮  │  ║
║  │                                                          │  ║
║  │  Model: KeeLoq RF Controller                            │  ║
║  │  Manufacturer: Jarolift                                 │  ║
║  │  Software version: 2.0.1                                │  ║
║  │  Firmware version: Not available                        │  ║
║  │                                                          │  ║
║  │  ▼ Entities (4)                                         │  ║
║  │  ┌──────────────────────────────────────────────────┐   │  ║
║  │  │  🪟 Living Room Cover               cover      ⚙️ │   │  ║
║  │  │  cover.living_room_cover                        │   │  ║
║  │  │  Closed                                         │   │  ║
║  │  └──────────────────────────────────────────────────┘   │  ║
║  │  ┌──────────────────────────────────────────────────┐   │  ║
║  │  │  🪟 Bedroom Cover                   cover      ⚙️ │   │  ║
║  │  │  cover.bedroom_cover                            │   │  ║
║  │  │  Open                                           │   │  ║
║  │  └──────────────────────────────────────────────────┘   │  ║
║  │  ┌──────────────────────────────────────────────────┐   │  ║
║  │  │  🪟 Kitchen Cover                   cover      ⚙️ │   │  ║
║  │  │  cover.kitchen_cover                            │   │  ║
║  │  │  Closed                                         │   │  ║
║  │  └──────────────────────────────────────────────────┘   │  ║
║  │  ┌──────────────────────────────────────────────────┐   │  ║
║  │  │  🪟 Office Cover                    cover      ⚙️ │   │  ║
║  │  │  cover.office_cover                             │   │  ║
║  │  │  Open                                           │   │  ║
║  │  └──────────────────────────────────────────────────┘   │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  SERVICES (4)                                                 ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │  • jarolift.send_raw                                   │  ║
║  │    Send a raw KeeLoq packet                            │  ║
║  │                                                        │  ║
║  │  • jarolift.send_command                               │  ║
║  │    Send a button command to a cover                    │  ║
║  │                                                        │  ║
║  │  • jarolift.learn                                      │  ║
║  │    Put a cover into learning mode                      │  ║
║  │                                                        │  ║
║  │  • jarolift.clear                                      │  ║
║  │    Clear a learned cover                               │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

## Comparison with Google Gemini Example

This matches the structure shown in the issue's Google Gemini screenshot:
- ✅ Device section at the top with metadata
- ✅ Expandable entities list beneath the device
- ✅ Services section listing available services
- ✅ Individual entity cards with controls
- ✅ Professional, organized appearance

## How This Works

The implementation uses Home Assistant's device registry pattern:

1. **Hub Device Created**: In `async_setup_entry()`, a device is registered:
   ```python
   device_registry.async_get_or_create(
       config_entry_id=entry.entry_id,
       identifiers={(DOMAIN, entry.entry_id)},
       name="Jarolift",
       manufacturer="Jarolift",
       model="KeeLoq RF Controller",
       sw_version="2.0.1",
   )
   ```

2. **Entities Linked to Device**: Each cover entity gets `device_info`:
   ```python
   self._attr_device_info = DeviceInfo(
       identifiers={(DOMAIN, entry_id)},
       name="Jarolift",
       manufacturer="Jarolift",
       model="KeeLoq RF Controller",
       sw_version="2.0.1",
   )
   ```

3. **Home Assistant Groups Automatically**: When Home Assistant sees entities with matching device identifiers, it automatically groups them under that device in the UI.

## User Benefits

✅ **No Configuration Needed**: Works automatically after upgrade
✅ **Better Organization**: All Jarolift entities in one logical group
✅ **Easy Navigation**: Quick access to all covers and services
✅ **Professional UI**: Matches Home Assistant's design standards
✅ **Device Management**: Can disable/remove all entities at once from device settings
✅ **Backward Compatible**: YAML configurations still work without UI changes

This implementation fully addresses the issue request to "list all entities in the integration UI" like the Google Gemini example.
