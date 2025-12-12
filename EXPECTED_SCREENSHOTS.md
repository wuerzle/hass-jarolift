# Expected UI Result - Screenshots Placeholder

## Note
Since we cannot actually run Home Assistant in this environment, these are mockups showing what the UI will look like when the feature is tested in a live Home Assistant instance.

## Screenshot 1: Options Menu with "Edit hub settings"

**Location:** Settings → Devices & Services → Jarolift → Configure

Expected to show:
```
┌─────────────────────────────────────────────────────┐
│ Manage Jarolift Covers                              │
├─────────────────────────────────────────────────────┤
│ Configure your Jarolift covers.                     │
│                                                      │
│ Currently configured covers:                        │
│ - Living Room Cover (Serial: 0x106aa01, Group: ...)│
│                                                      │
│ Action: [Dropdown ▼]                                │
│   • Add new cover                                   │
│   • Edit existing cover                             │
│   • Remove cover                                    │
│   • Edit hub settings    ← NEW!                     │
│   • Finish                                          │
│                                                      │
│ [SUBMIT]                                            │
└─────────────────────────────────────────────────────┘
```

## Screenshot 2: Edit Hub Settings Form

**Location:** After selecting "Edit hub settings" and clicking Submit

Expected to show:
```
┌─────────────────────────────────────────────────────┐
│ Edit Hub Settings                                    │
├─────────────────────────────────────────────────────┤
│ Modify the Jarolift hub configuration. Changes will │
│ apply after reloading the integration.              │
│                                                      │
│ Remote Entity ID *                                   │
│ ┌───────────────────────────────────────────────┐  │
│ │ remote.broadlink_rm_proplus_remote            │  │
│ └───────────────────────────────────────────────┘  │
│ The entity ID of your remote                        │
│                                                      │
│ Manufacturer Key MSB (Most Significant Bits) *      │
│ ┌───────────────────────────────────────────────┐  │
│ │ 0x12345678                                     │  │
│ └───────────────────────────────────────────────┘  │
│ The MSB part of the manufacturer key                │
│                                                      │
│ Manufacturer Key LSB (Least Significant Bits) *     │
│ ┌───────────────────────────────────────────────┐  │
│ │ 0x87654321                                     │  │
│ └───────────────────────────────────────────────┘  │
│ The LSB part of the manufacturer key                │
│                                                      │
│ Delay between commands (seconds)                    │
│ ┌───────────────────────────────────────────────┐  │
│ │ 0                                              │  │
│ └───────────────────────────────────────────────┘  │
│ Optional delay between sending commands             │
│                                                      │
│ [SUBMIT]                                            │
└─────────────────────────────────────────────────────┘
```

## Screenshot 3: Error Display (Invalid Remote Entity)

**Location:** After submitting with invalid remote entity

Expected to show:
```
┌─────────────────────────────────────────────────────┐
│ Edit Hub Settings                                    │
├─────────────────────────────────────────────────────┤
│ ⚠️ Error: Remote Entity ID                          │
│ The specified remote entity does not exist          │
│                                                      │
│ Remote Entity ID *                                   │
│ ┌───────────────────────────────────────────────┐  │
│ │ remote.nonexistent        ⚠️                   │  │
│ └───────────────────────────────────────────────┘  │
│ The entity ID of your remote                        │
│                                                      │
│ [... other fields unchanged ...]                    │
│                                                      │
│ [SUBMIT]                                            │
└─────────────────────────────────────────────────────┘
```

## Screenshot 4: Success (Return to Menu)

**Location:** After successful submission

Expected behavior:
- Form closes
- Returns to "Manage Jarolift Covers" menu
- Integration reloads in background
- Toast notification may appear: "Configuration updated"

## Screenshot 5: German Translation

**Location:** Same as Screenshot 2, but with German language

Expected to show:
```
┌─────────────────────────────────────────────────────┐
│ Hub-Einstellungen bearbeiten                         │
├─────────────────────────────────────────────────────┤
│ Ändern Sie die Jarolift Hub-Konfiguration. Die     │
│ Änderungen werden nach dem Neuladen der Integration│
│ wirksam.                                            │
│                                                      │
│ Fernbedienungs-Entitäts-ID *                        │
│ ┌───────────────────────────────────────────────┐  │
│ │ remote.broadlink_rm_proplus_remote            │  │
│ └───────────────────────────────────────────────┘  │
│ Die Entitäts-ID Ihrer Fernbedienung                 │
│                                                      │
│ [... German translations for all fields ...]        │
│                                                      │
│ [SENDEN]                                            │
└─────────────────────────────────────────────────────┘
```

## How to Capture Actual Screenshots

When testing in Home Assistant:

1. **Navigate to the feature:**
   - Settings → Devices & Services
   - Find Jarolift integration
   - Click "CONFIGURE"

2. **Capture screenshots:**
   - Use browser screenshot tool (F12 → Device Toolbar → Screenshot)
   - Or use OS screenshot tool (Windows: Win+Shift+S, Mac: Cmd+Shift+4)
   - Save as PNG format

3. **Recommended screenshots to capture:**
   - `01-options-menu.png` - Main menu with "Edit hub settings"
   - `02-edit-hub-form-empty.png` - Form on first display
   - `03-edit-hub-form-filled.png` - Form with modified values
   - `04-validation-error.png` - Error display
   - `05-german-translation.png` - German UI
   - `06-after-update.png` - Return to menu after success

4. **Add screenshots to PR:**
   - Upload to PR comment
   - Or commit to `docs/screenshots/` directory
   - Reference in PR description

## Testing Checklist

When capturing screenshots, verify:

- [ ] "Edit hub settings" visible in dropdown
- [ ] Form title and description display correctly
- [ ] All fields show pre-filled values
- [ ] Help text appears below each field
- [ ] Required fields marked with asterisk (*)
- [ ] Submit button is present
- [ ] Error messages display clearly
- [ ] Form reappears with errors (doesn't close)
- [ ] German translation complete and accurate
- [ ] UI follows Home Assistant design patterns
- [ ] Responsive design (test on mobile if possible)

## Expected User Experience

1. **Discovery:** User finds "Edit hub settings" in familiar options menu
2. **Recognition:** User sees current values pre-filled (reduces errors)
3. **Confidence:** Help text explains each field clearly
4. **Safety:** Validation prevents invalid configurations
5. **Feedback:** Clear error messages guide user to fix issues
6. **Success:** Automatic return to menu confirms update
7. **Transparency:** User knows integration will reload

## Accessibility Notes

The UI should support:
- Keyboard navigation (Tab, Enter, Escape)
- Screen readers (proper ARIA labels)
- High contrast mode
- Focus indicators
- Form validation messages

These will be automatically provided by Home Assistant's UI framework.

---

**Note:** Actual screenshots will be added after manual testing in a live Home Assistant environment. The mockups above represent the expected appearance based on the implementation.
