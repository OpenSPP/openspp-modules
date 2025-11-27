## Bugfix: Archive Notification Message

### Issue
Odoo core has a bug in the archive notification where the parameters are swapped, showing an illogical message like:
> "Of the 20,000 records selected, only the first 50,000 have been archived/unarchived."

This is impossible since you cannot archive more records than were selected.

### Root Cause
**Location**: `odoo/addons/web/static/src/legacy/js/views/list/list_controller.js:658-659`

**Bug**: The sprintf parameters are in the wrong order:
```javascript
const msg = _.str.sprintf(
    _t("Of the %d records selected, only the first %d have been archived/unarchived."),
    total, resIds.length  // ← WRONG ORDER
);
```

### Fix
This module patches the `ListController._toggleArchiveState` method to swap the parameters:
```javascript
const msg = _.str.sprintf(
    _t("Of the %d records selected, only the first %d have been archived/unarchived."),
    resIds.length, total  // ← CORRECT ORDER  
);
```

### Result
After the fix, the notification correctly shows:
> "Of the 50,000 records selected, only the first 20,000 have been archived/unarchived."

### References
- Odoo Repository: https://github.com/odoo/odoo/tree/17.0/odoo/addons/base
- Fixed in: `spp_base_common/static/src/legacy/js/views/list/list_controller_fix.js`

