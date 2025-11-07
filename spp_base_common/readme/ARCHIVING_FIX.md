## Archiving Notification Fix

### Issue
The global Odoo archiving method had swapped notification parameters, showing messages like:
"50,000 records have been archived out of 20,000 selected"

This is illogical as you cannot archive more records than were selected.

### Solution
This module overrides the `_toggleArchiveState` method in the legacy ListController to fix the swapped parameters in the notification message.

The fix swaps the parameters from `(total, resIds.length)` to `(resIds.length, total)` to correctly display:
"Of the [number_selected] records selected, only the first [number_archived] have been archived/unarchived."

### Technical Details
- **File**: `static/src/js/list_controller.js`
- **Method**: `_toggleArchiveState`
- **Original Location**: `addons/web/static/src/legacy/js/views/list/list_controller.js` (line 658-659)

