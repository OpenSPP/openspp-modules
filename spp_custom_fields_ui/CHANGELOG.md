# Changelog

## 2025-11-20

### 2025-11-20 15:00:00 - [FIX] test_13_onchange_has_presence to use correct field type

- Changed field type from integer to boolean to match has_presence=True
- Prevents UserError about unsupported type changes during test execution
- Ensures test covers \_onchange_has_presence method without triggering errors

### 2025-11-20 14:45:00 - [ADD] tests for onchange methods in custom fields UI

- Added test_10_onchange_field_category to test field category changes
- Added test_11_onchange_kinds to test kinds assignment updates
- Added test_12_onchange_target_type to test target type changes
- Added test_13_onchange_has_presence to test presence flag changes
- Improves codecov coverage for onchange methods

### 2025-11-20 10:24:55 - [FIX] add safety check to prevent reload on wrong page after navigation

- Added URL verification before executing scheduled page reload
- Prevents reload on wrong page if user navigates away during 100ms timeout
- Only reloads if user is still on ir.model.fields page
- Protects against data loss on unrelated pages

### 2025-11-20 10:12:34 - [FIX] remove meaningless return after page reload in custom fields UI

- Fixed bug where return statement after window.location.reload() was unreachable
- For existing records, reload happens immediately before return, destroying page context
- For new records, setTimeout creates race condition where return value is meaningless
- Added proper handling for result === false case without reload
- Added comments explaining control flow in reload scenarios
