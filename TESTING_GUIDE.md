# Testing Guide for Hub Configuration UI

This guide provides instructions for manually testing the new "Edit hub settings" feature.

## Prerequisites

1. Home Assistant 2022.2 or higher installed
2. Jarolift integration installed with the new changes
3. At least one RF remote entity configured (e.g., Broadlink)
4. Access to Home Assistant UI

## Test Environment Setup

### Option 1: Test with Real Hardware
- Broadlink RM Pro+ or similar RF remote
- At least one Jarolift cover
- Manufacturer key (MSB/LSB)

### Option 2: Test with Mock Remote (UI testing only)
- Create a mock remote entity in Home Assistant
- Use placeholder manufacturer keys
- Note: Commands won't actually work, but UI can be tested

## Test Cases

### Test Case 1: Access Edit Hub Settings

**Objective:** Verify the new menu option appears

**Steps:**
1. Navigate to Settings → Devices & Services
2. Find the Jarolift integration card
3. Click "CONFIGURE" button
4. Verify the "Action" dropdown shows: "Edit hub settings"

**Expected Result:**
- ✅ "Edit hub settings" option is visible in the dropdown
- ✅ Other options (Add, Edit, Remove, Finish) are still present

**Screenshot Location:** Save as `test-case-1-menu.png`

---

### Test Case 2: Display Edit Hub Form

**Objective:** Verify the form displays with pre-filled values

**Steps:**
1. From the manage covers menu, select "Edit hub settings"
2. Click "SUBMIT"
3. Observe the form that appears

**Expected Result:**
- ✅ Form title: "Edit Hub Settings"
- ✅ Form description mentions changes apply after reload
- ✅ Remote Entity ID field shows current value
- ✅ MSB field shows current value
- ✅ LSB field shows current value
- ✅ Delay field shows current value (default: 0)
- ✅ All fields have help text below them

**Screenshot Location:** Save as `test-case-2-form.png`

---

### Test Case 3: Update Remote Entity ID

**Objective:** Verify changing remote entity ID works

**Pre-requisites:**
- Two remote entities available (e.g., `remote.rm_mini` and `remote.rm_pro`)

**Steps:**
1. Note the current remote entity ID
2. Open edit hub settings form
3. Change Remote Entity ID to a different valid remote entity
4. Click "SUBMIT"
5. Verify you return to manage covers menu
6. Check Home Assistant logs for reload message
7. Test cover operation (if using real hardware)

**Expected Result:**
- ✅ Form accepts the new remote entity ID
- ✅ No error messages appear
- ✅ Returns to manage covers menu
- ✅ Integration reloads automatically
- ✅ Covers use new remote entity for commands

**Screenshot Location:** Save as `test-case-3-success.png`

---

### Test Case 4: Invalid Remote Entity ID

**Objective:** Verify validation of remote entity ID

**Steps:**
1. Open edit hub settings form
2. Change Remote Entity ID to `remote.nonexistent_device`
3. Click "SUBMIT"
4. Observe the error message

**Expected Result:**
- ✅ Form redisplays with error
- ✅ Error message: "The specified remote entity does not exist"
- ✅ Red indicator or warning icon near the field
- ✅ All other fields retain their values
- ✅ No changes saved to configuration

**Screenshot Location:** Save as `test-case-4-error.png`

---

### Test Case 5: Update Manufacturer Keys

**Objective:** Verify MSB and LSB can be updated

**Steps:**
1. Open edit hub settings form
2. Change MSB value (e.g., from `0x12345678` to `0xAABBCCDD`)
3. Change LSB value (e.g., from `0x87654321` to `0xDDCCBBAA`)
4. Keep Remote Entity ID unchanged
5. Click "SUBMIT"
6. Test cover operation (if using real hardware with correct keys)

**Expected Result:**
- ✅ Form accepts hex string format
- ✅ No error messages
- ✅ Returns to manage covers menu
- ✅ Integration reloads
- ✅ If keys are correct, covers operate normally
- ✅ If keys are incorrect, covers don't respond (expected)

**Note:** Use real manufacturer keys if testing with actual hardware.

**Screenshot Location:** Save as `test-case-5-msb-lsb.png`

---

### Test Case 6: Update Delay Parameter

**Objective:** Verify delay parameter can be modified

**Pre-requisites:**
- Multiple covers configured

**Steps:**
1. Open edit hub settings form
2. Change Delay from 0 to 2 (seconds)
3. Click "SUBMIT"
4. Test multiple cover operations in sequence
5. Observe timing between commands

**Expected Result:**
- ✅ Form accepts integer value
- ✅ No error messages
- ✅ Returns to manage covers menu
- ✅ Integration reloads
- ✅ 2-second delay observed between cover commands

**Verification Method:**
- Watch Home Assistant logs for command timestamps
- Or use stopwatch while operating multiple covers

**Screenshot Location:** Save as `test-case-6-delay.png`

---

### Test Case 7: Cancel Without Changes

**Objective:** Verify canceling preserves original values

**Steps:**
1. Open edit hub settings form
2. Note the current values
3. Make changes to one or more fields
4. Navigate back (browser back button or close dialog)
5. Re-open edit hub settings form
6. Verify values are unchanged

**Expected Result:**
- ✅ Original values are still displayed
- ✅ No changes were saved
- ✅ No integration reload occurred

---

### Test Case 8: German Translation

**Objective:** Verify German translations display correctly

**Pre-requisites:**
- Home Assistant user profile set to German language

**Steps:**
1. Change Home Assistant language to German (Profile → Language)
2. Navigate to Jarolift integration configuration
3. Select "Hub-Einstellungen bearbeiten" (Edit hub settings)
4. Observe the form

**Expected Result:**
- ✅ Title: "Hub-Einstellungen bearbeiten"
- ✅ Description in German
- ✅ Field labels in German:
  - "Fernbedienungs-Entitäts-ID"
  - "Herstellerschlüssel MSB"
  - "Herstellerschlüssel LSB"
  - "Verzögerung zwischen Befehlen"
- ✅ Help text in German

**Screenshot Location:** Save as `test-case-8-german.png`

---

### Test Case 9: Integration Reload Behavior

**Objective:** Verify integration reloads after hub settings update

**Steps:**
1. Open Home Assistant logs (Settings → System → Logs)
2. Filter for "jarolift"
3. Open edit hub settings form
4. Change any value
5. Click "SUBMIT"
6. Watch the logs

**Expected Result:**
- ✅ Log entry: "Setting up jarolift" or similar reload message
- ✅ Log entry: "Jarolift integration reloaded"
- ✅ No error messages
- ✅ Services remain registered
- ✅ Covers remain available

**Log Entries to Check:**
```
DEBUG homeassistant.config_entries: ...
INFO custom_components.jarolift: ...
```

---

### Test Case 10: Multiple Sequential Updates

**Objective:** Verify multiple updates work correctly

**Steps:**
1. Update remote entity ID → Submit → Verify success
2. Return to edit hub settings
3. Update MSB → Submit → Verify success
4. Return to edit hub settings
5. Update LSB → Submit → Verify success
6. Return to edit hub settings
7. Update Delay → Submit → Verify success

**Expected Result:**
- ✅ Each update succeeds independently
- ✅ No accumulated errors
- ✅ Final configuration has all updates applied
- ✅ Integration remains stable

---

### Test Case 11: Persistence After Restart

**Objective:** Verify updated hub settings persist across Home Assistant restart

**Steps:**
1. Update any hub setting
2. Note the new value
3. Restart Home Assistant
4. After restart, open edit hub settings form
5. Verify the form shows the updated value

**Expected Result:**
- ✅ Updated values are retained after restart
- ✅ Integration loads with new configuration
- ✅ Covers continue to work

---

## Regression Testing

Verify existing functionality still works:

### Regression Test 1: Add Cover
- ✅ Can still add new covers
- ✅ Cover appears in Home Assistant
- ✅ Cover operates correctly

### Regression Test 2: Edit Cover
- ✅ Can still edit existing covers
- ✅ Changes are saved
- ✅ Cover operates with new settings

### Regression Test 3: Remove Cover
- ✅ Can still remove covers
- ✅ Cover disappears from Home Assistant
- ✅ No errors in logs

### Regression Test 4: Services
- ✅ `jarolift.send_command` service works
- ✅ `jarolift.send_raw` service works
- ✅ `jarolift.learn` service works
- ✅ `jarolift.clear` service works

---

## Test Report Template

```markdown
# Hub Configuration UI Test Report

**Date:** YYYY-MM-DD
**Tester:** [Name]
**Home Assistant Version:** [Version]
**Jarolift Integration Version:** [Commit/Tag]
**Hardware:** [Real/Mock]

## Test Results Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC1: Access Menu | ✅/❌ | |
| TC2: Display Form | ✅/❌ | |
| TC3: Update Remote | ✅/❌ | |
| TC4: Invalid Remote | ✅/❌ | |
| TC5: Update Keys | ✅/❌ | |
| TC6: Update Delay | ✅/❌ | |
| TC7: Cancel | ✅/❌ | |
| TC8: German Translation | ✅/❌ | |
| TC9: Reload | ✅/❌ | |
| TC10: Multiple Updates | ✅/❌ | |
| TC11: Persistence | ✅/❌ | |
| RT1: Add Cover | ✅/❌ | |
| RT2: Edit Cover | ✅/❌ | |
| RT3: Remove Cover | ✅/❌ | |
| RT4: Services | ✅/❌ | |

## Issues Found

[List any issues or bugs discovered during testing]

## Screenshots

[Attach screenshots for each test case]

## Additional Notes

[Any other observations or comments]
```

---

## Troubleshooting

### Issue: "Edit hub settings" option not visible
**Solution:**
- Verify you're using the updated version of the integration
- Check browser cache (force refresh: Ctrl+F5)
- Verify `config_flow.py` has been updated

### Issue: Form shows empty fields
**Solution:**
- Check Home Assistant logs for errors
- Verify config entry has data populated
- Check that `self.config_entry` is being stored in `__init__`

### Issue: Changes not persisted
**Solution:**
- Check Home Assistant logs for errors during reload
- Verify `async_update_entry` is being called
- Check file permissions on `.storage` directory

### Issue: Integration doesn't reload
**Solution:**
- Check for errors in Home Assistant logs
- Verify `async_reload_entry` is registered as update listener
- Manually reload integration from UI

---

## Success Criteria

All test cases must pass:
- ✅ UI displays correctly
- ✅ Validation works properly
- ✅ Changes are saved
- ✅ Integration reloads automatically
- ✅ Covers continue to function
- ✅ No errors in logs
- ✅ Translations work correctly
- ✅ Existing functionality not broken

---

## Additional Testing Notes

- Test with both mock and real hardware if possible
- Test with different Home Assistant themes (light/dark)
- Test on different browsers (Chrome, Firefox, Safari)
- Test on mobile devices (responsive design)
- Check accessibility (keyboard navigation, screen readers)

---

## Reporting Issues

If you find any issues during testing, please report them with:
1. Test case number
2. Steps to reproduce
3. Expected vs actual behavior
4. Screenshots
5. Home Assistant logs (if relevant)
6. Browser/device information
