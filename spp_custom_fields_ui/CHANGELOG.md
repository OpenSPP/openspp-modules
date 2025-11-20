# Changelog

## 2025-11-20

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
