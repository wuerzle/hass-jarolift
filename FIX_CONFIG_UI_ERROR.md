# Fix: Config UI Error When Editing Hub Settings

## Issue Description
When editing hub settings through the configuration UI, Home Assistant would get stuck if the user entered an invalid remote entity. The UI would not display the error message and would become unresponsive.

## Root Cause
The issue was caused by a missing error translation. The `async_step_edit_hub` method in `config_flow.py` was trying to display the error `invalid_remote_entity` when validating the remote entity, but this error string was only defined in the `config.error` section of the translation files, not in the `options.error` section where it was needed.

When Home Assistant's config flow system tried to look up the error message at `options.error.invalid_remote_entity`, it couldn't find it, which caused the UI to fail silently and get stuck.

## The Fix
Added the missing error translation to both English and German translation files:

### strings.json
```json
"options": {
  ...
  "error": {
    "duplicate_cover": "A cover with this serial and group combination already exists",
    "invalid_remote_entity": "The specified remote entity does not exist"
  }
}
```

### translations/de.json
```json
"options": {
  ...
  "error": {
    "duplicate_cover": "Ein Rollo mit dieser Serien- und Gruppenkombination existiert bereits",
    "invalid_remote_entity": "Die angegebene Fernbedienungs-Entität existiert nicht"
  }
}
```

## Files Modified
1. `custom_components/jarolift/strings.json` - Added `invalid_remote_entity` error to `options.error`
2. `custom_components/jarolift/translations/de.json` - Added `invalid_remote_entity` error to `options.error`
3. `tests/test_config_flow.py` - Added two test cases to verify the fix

## Testing
Added two new test cases:
1. `test_options_flow_edit_hub_valid` - Verifies that editing hub settings with a valid remote entity works correctly
2. `test_options_flow_edit_hub_invalid_remote` - Verifies that the error is properly displayed when an invalid remote entity is provided

## Impact
This fix ensures that:
- Users can now see the error message when they enter an invalid remote entity ID
- The UI no longer gets stuck when validation fails
- The error message is properly localized for both English and German users

## Prevention
This type of issue can be prevented by:
1. Ensuring all error codes used in config flows are defined in both `config.error` and `options.error` sections
2. Adding tests for all error scenarios in the config flow
3. Reviewing translation files when adding new validation logic
