# Hub Configuration UI - Visual Flow

This document shows what users will see when using the new "Edit hub settings" feature.

## Step 1: Navigate to Integration Configuration

**Path:** Settings → Devices & Services → Jarolift Integration

The user clicks on the **"CONFIGURE"** button on the Jarolift integration card.

---

## Step 2: Manage Covers Menu (Main Options Menu)

```
┌────────────────────────────────────────────────────────┐
│ Manage Jarolift Covers                                 │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Configure your Jarolift covers.                        │
│                                                         │
│ Currently configured covers:                           │
│ - Living Room Cover (Serial: 0x106aa01, Group: 0x0001)│
│ - Bedroom Cover (Serial: 0x106aa02, Group: 0x0001)    │
│                                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Action: [Dropdown Menu ▼]                             │
│                                                         │
│   • Add new cover                                      │
│   • Edit existing cover                                │
│   • Remove cover                                       │
│   • Edit hub settings          ← NEW OPTION           │
│   • Finish                                             │
│                                                         │
├────────────────────────────────────────────────────────┤
│                         [SUBMIT]                        │
└────────────────────────────────────────────────────────┘
```

When the user selects **"Edit hub settings"** and clicks SUBMIT, they proceed to Step 3.

---

## Step 3: Edit Hub Settings Form

```
┌────────────────────────────────────────────────────────┐
│ Edit Hub Settings                                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Modify the Jarolift hub configuration. Changes will    │
│ apply after reloading the integration.                 │
│                                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Remote Entity ID *                                     │
│ ┌─────────────────────────────────────────────────┐  │
│ │ remote.broadlink_rm_proplus_remote              │  │
│ └─────────────────────────────────────────────────┘  │
│ The entity ID of your remote (e.g.,                   │
│ remote.broadlink_rm_proplus_remote)                   │
│                                                         │
│ Manufacturer Key MSB (Most Significant Bits) *        │
│ ┌─────────────────────────────────────────────────┐  │
│ │ 0x12345678                                       │  │
│ └─────────────────────────────────────────────────┘  │
│ The MSB part of the manufacturer key in hex format    │
│ (e.g., '0x12345678')                                  │
│                                                         │
│ Manufacturer Key LSB (Least Significant Bits) *       │
│ ┌─────────────────────────────────────────────────┐  │
│ │ 0x87654321                                       │  │
│ └─────────────────────────────────────────────────┘  │
│ The LSB part of the manufacturer key in hex format    │
│ (e.g., '0x87654321')                                  │
│                                                         │
│ Delay between commands (seconds)                       │
│ ┌─────────────────────────────────────────────────┐  │
│ │ 0                                                 │  │
│ └─────────────────────────────────────────────────┘  │
│ Optional delay between sending commands to            │
│ different covers                                       │
│                                                         │
├────────────────────────────────────────────────────────┤
│                         [SUBMIT]                        │
└────────────────────────────────────────────────────────┘
```

### Form Features:
- **Pre-filled values**: All fields show current configuration
- **Required fields**: Remote Entity ID, MSB, and LSB are required
- **Optional field**: Delay (defaults to 0)
- **Help text**: Each field has descriptive help text below it

---

## Step 4A: Successful Update

After clicking SUBMIT with valid values:

```
┌────────────────────────────────────────────────────────┐
│ ✓ Hub settings updated successfully                    │
│                                                         │
│ The integration will reload automatically.             │
└────────────────────────────────────────────────────────┘
```

The user is automatically returned to the "Manage Covers" menu (Step 2).

---

## Step 4B: Validation Error

If the user enters an invalid remote entity ID:

```
┌────────────────────────────────────────────────────────┐
│ Edit Hub Settings                                       │
├────────────────────────────────────────────────────────┤
│ ⚠️ Error                                                │
│                                                         │
│ Remote Entity ID: The specified remote entity does     │
│                   not exist                            │
│                                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Remote Entity ID *                                     │
│ ┌─────────────────────────────────────────────────┐  │
│ │ remote.nonexistent_device        ⚠️             │  │
│ └─────────────────────────────────────────────────┘  │
│ The entity ID of your remote (e.g.,                   │
│ remote.broadlink_rm_proplus_remote)                   │
│                                                         │
│ [... other fields ...]                                 │
│                                                         │
├────────────────────────────────────────────────────────┤
│                         [SUBMIT]                        │
└────────────────────────────────────────────────────────┘
```

The form is redisplayed with the error message, and the user can correct the input.

---

## Use Cases

### 1. Changing Remote Entity
**Scenario:** User upgraded from Broadlink RM Mini to Broadlink RM Pro+

**Before this feature:**
- User must delete entire Jarolift integration
- Lose all cover configurations
- Re-add integration with new remote entity
- Re-configure all covers manually

**With this feature:**
1. Click CONFIGURE on Jarolift integration
2. Select "Edit hub settings"
3. Change Remote Entity ID from `remote.broadlink_rm_mini` to `remote.broadlink_rm_proplus_remote`
4. Click SUBMIT
5. Done! All covers continue working with the new remote.

### 2. Fixing Manufacturer Key Typo
**Scenario:** User accidentally entered wrong MSB/LSB during initial setup

**Before this feature:**
- Delete and recreate integration
- Reconfigure all covers

**With this feature:**
1. Click CONFIGURE on Jarolift integration
2. Select "Edit hub settings"
3. Correct the MSB or LSB value
4. Click SUBMIT
5. Covers now work properly!

### 3. Adjusting Delay
**Scenario:** User wants to add delay between cover commands to avoid interference

**Before this feature:**
- Edit configuration.yaml (if using YAML)
- Or delete and recreate integration

**With this feature:**
1. Click CONFIGURE on Jarolift integration
2. Select "Edit hub settings"
3. Change Delay from 0 to 2 seconds
4. Click SUBMIT
5. Commands now have 2-second delay between covers.

---

## German Translation Example

When Home Assistant is set to German language:

```
┌────────────────────────────────────────────────────────┐
│ Hub-Einstellungen bearbeiten                           │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Ändern Sie die Jarolift Hub-Konfiguration. Die        │
│ Änderungen werden nach dem Neuladen der Integration   │
│ wirksam.                                               │
│                                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│ Fernbedienungs-Entitäts-ID *                          │
│ ┌─────────────────────────────────────────────────┐  │
│ │ remote.broadlink_rm_proplus_remote              │  │
│ └─────────────────────────────────────────────────┘  │
│ Die Entitäts-ID Ihrer Fernbedienung (z.B.            │
│ remote.broadlink_rm_proplus_remote)                   │
│                                                         │
│ Herstellerschlüssel MSB (Most Significant Bits) *     │
│ [...]                                                   │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## Implementation Notes

### Backend Changes
- New method: `async_step_edit_hub()` in `JaroliftOptionsFlow`
- Uses `hass.config_entries.async_update_entry()` to save changes
- Validates remote entity exists before saving
- Automatic integration reload via `async_reload_entry`

### Data Storage
- Hub parameters stored in `config_entry.data`
- Cover configurations stored in `config_entry.options`
- This separation maintains architectural consistency

### Validation
- Remote entity ID: Must exist in Home Assistant states
- MSB/LSB: Accept hex string format (e.g., '0x12345678')
- Delay: Coerced to integer, defaults to 0

---

## Testing Recommendations

Manual testing should verify:

1. ✅ "Edit hub settings" appears in options menu
2. ✅ Form displays with current values pre-filled
3. ✅ Valid changes save successfully
4. ✅ Invalid remote entity shows error and redisplays form
5. ✅ Integration reloads after successful update
6. ✅ Covers use the new remote entity for sending commands
7. ✅ Services use the new MSB/LSB values for encryption
8. ✅ Delay parameter affects timing between cover commands
9. ✅ UI strings display correctly in English
10. ✅ UI strings display correctly in German

---

## Summary

This feature completes the UI configuration experience by allowing users to modify hub parameters without losing their cover configurations. It follows Home Assistant's best practices for configuration flows and provides a seamless user experience.
