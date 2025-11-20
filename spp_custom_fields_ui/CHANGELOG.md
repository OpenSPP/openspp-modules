# Changelog

## 2025-11-20

### 2025-11-20 10:12:34 - [FIX] remove meaningless return after page reload in custom fields UI
- Fixed bug where return statement after window.location.reload() was unreachable
- For existing records, reload happens immediately before return, destroying page context
- For new records, setTimeout creates race condition where return value is meaningless
- Added proper handling for result === false case without reload
- Added comments explaining control flow in reload scenarios

