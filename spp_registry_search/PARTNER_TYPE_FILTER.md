# Partner Type Filter Enhancement

## Overview

Enhanced the Partner Custom Search feature to include a **Partner Type** selector that allows users to filter searches between Individuals and Groups. Additionally, the search now **always filters by `is_registrant=True`** to ensure only registrant partners are returned.

## Changes Made

### 1. Frontend (JavaScript)

**File:** `static/src/js/partner_search_view.js`

**Added:**
- New state property: `partnerType` (default: "individual")
- New method: `onPartnerTypeChange(event)` - handles partner type selection
- Updated `onSearch()` to pass `is_group` parameter to backend
- Updated `onClearSearch()` to reset partner type to "individual"

**Code:**
```javascript
this.state = useState({
    searchFields: [],
    selectedField: "",
    searchValue: "",
    partnerType: "individual", // NEW
    searching: false,
    results: [],
    showResults: false,
});

// Determine is_group value based on partner type
const isGroup = this.state.partnerType === "group";

const results = await this.orm.call(
    "res.partner",
    "search_by_field",
    [this.state.selectedField, this.state.searchValue, isGroup] // Added isGroup parameter
);
```

### 2. Frontend (Template)

**File:** `static/src/xml/partner_search_view.xml`

**Added:**
- New Partner Type dropdown field with "Individual" and "Group" options
- Adjusted column layout (col-md-4 → col-md-3 for first two fields, col-md-5 → col-md-4 for search value, col-md-3 → col-md-2 for button)
- New "Type" column in results table showing badge (Group = blue, Individual = green)
- Updated help text to mention partner type selection

**UI Layout:**
```
[Partner Type ▼] [Search Field ▼] [Search Value [____]] [Search]
   col-md-3         col-md-3          col-md-4         col-md-2
```

**Results Table:**
```
| Type | Name | Email | Phone | Mobile | City | Country | Actions |
```

### 3. Backend (Python)

**File:** `models/res_partner.py`

**Updated `search_by_field` method:**
- Added `is_group` parameter (default: `False`)
- Added domain filter: `("is_group", "=", is_group)`
- Added domain filter: `("is_registrant", "=", True)` - **ALWAYS APPLIED**
- Updated docstring

**Signature:**
```python
@api.model
def search_by_field(self, field_name, search_value, is_group=False):
    """
    Search partners by a specific field
    :param field_name: The field name to search on
    :param search_value: The value to search for
    :param is_group: Whether to search for groups (True) or individuals (False)
    :return: List of matching partner IDs
    """
    # ... field-specific domain building ...
    
    # Add partner type filter (is_group)
    domain.append(("is_group", "=", is_group))
    
    # Always filter by is_registrant = True
    domain.append(("is_registrant", "=", True))
    
    return self.search(domain).ids
```

### 4. Tests

**File:** `tests/test_partner_search.py`

**Updated:**
- Added test group creation in `setUpClass`
- Updated all search tests to pass `is_group` parameter
- Enhanced `test_03_search_by_name` to test both individuals and groups
- Added new test: `test_11_is_registrant_filter` to verify registrant filtering

**Test Coverage:**
```python
# Test searching for individuals
partner_ids = self.env["res.partner"].search_by_field(
    "name", "Test Partner", is_group=False
)

# Test searching for groups
group_ids = self.env["res.partner"].search_by_field(
    "name", "Test Group", is_group=True
)

# Test is_registrant filter
# Creates non-registrant partner and verifies it's NOT returned
```

### 5. Documentation

**Updated Files:**
- `QUICK_REFERENCE.md` - Updated API examples and use cases
- Added this file: `PARTNER_TYPE_FILTER.md`

## Features

### ✨ Key Features

1. **Partner Type Selector**
   - Dropdown with "Individual" (default) and "Group" options
   - Visually distinct with users icon
   - Persists during search session

2. **Automatic Domain Filtering**
   - `is_group`: Filtered based on user selection
   - `is_registrant`: ALWAYS set to `True` (cannot be disabled)

3. **Visual Type Indicators**
   - Green badge with user icon for Individuals
   - Blue badge with users icon for Groups
   - Shows in results table first column

4. **Backward Compatible**
   - Default parameter `is_group=False` maintains backward compatibility
   - Existing code without the parameter still works

## Usage Examples

### For End Users

**Search for an Individual:**
1. Select "Individual" from Partner Type
2. Select "Name" from Search Field
3. Enter "John"
4. Click Search
5. Results show only individuals with `is_registrant=True`

**Search for a Group:**
1. Select "Group" from Partner Type
2. Select "Name" from Search Field
3. Enter "Smith Family"
4. Click Search
5. Results show only groups with `is_registrant=True`

### For Developers

**Python:**
```python
# Search for individual registrants
individual_ids = env['res.partner'].search_by_field('name', 'John', is_group=False)

# Search for group registrants
group_ids = env['res.partner'].search_by_field('name', 'Smith', is_group=True)

# Default is individual (backward compatible)
partner_ids = env['res.partner'].search_by_field('email', 'test@example.com')
```

**JavaScript:**
```javascript
// Search for individuals
const individuals = await this.orm.call(
    'res.partner',
    'search_by_field',
    ['name', 'John', false]
);

// Search for groups
const groups = await this.orm.call(
    'res.partner',
    'search_by_field',
    ['name', 'Smith Family', true]
);
```

## Domain Filter Details

Every search now applies these filters:

```python
domain = [
    (field_name, operator, search_value),  # Field-specific search
    ("is_group", "=", is_group),           # Partner type filter
    ("is_registrant", "=", True),          # Always applied
]
```

**Example domain for searching individual's name:**
```python
[
    ("name", "ilike", "John"),
    ("is_group", "=", False),
    ("is_registrant", "=", True),
]
```

**Example domain for searching group's email:**
```python
[
    ("email", "ilike", "family@example.com"),
    ("is_group", "=", True),
    ("is_registrant", "=", True),
]
```

## Benefits

### 1. **Better Search Precision**
- Users can specifically target individuals or groups
- Reduces irrelevant results

### 2. **Registrant-Only Results**
- Ensures only registry members appear in search
- Automatic filtering prevents accidental inclusion of non-registrants

### 3. **Clear Visual Feedback**
- Color-coded badges make it obvious what type each result is
- Consistent iconography (user vs users)

### 4. **Improved UX**
- One-click partner type selection
- No need to manually add type filters
- Cleaner, more organized search interface

## Testing

### Manual Testing

1. **Test Individual Search:**
   - Select "Individual"
   - Search by name
   - Verify only individuals appear with green badge

2. **Test Group Search:**
   - Select "Group"
   - Search by name
   - Verify only groups appear with blue badge

3. **Test Registrant Filter:**
   - Create a non-registrant partner (is_registrant=False)
   - Search for it
   - Verify it does NOT appear in results

### Automated Testing

Run the test suite:
```bash
odoo-bin -u spp_base_common --test-enable --stop-after-init -d your_database
```

11 tests now cover:
- Individual search
- Group search
- Mixed searches
- Registrant filtering
- Edge cases

## Migration Notes

### Upgrading from Previous Version

**No breaking changes!**

- Existing functionality preserved
- New parameter has default value
- Frontend automatically uses new feature
- Backend backward compatible

### API Changes

**Before:**
```python
search_by_field(field_name, search_value)
```

**After:**
```python
search_by_field(field_name, search_value, is_group=False)
```

The third parameter is **optional** with a default value, so existing code continues to work.

## Technical Details

### State Management

JavaScript component state:
```javascript
{
    searchFields: [],        // Available fields from backend
    selectedField: "",       // Currently selected field
    searchValue: "",         // User's search input
    partnerType: "individual", // NEW: "individual" or "group"
    searching: false,        // Loading state
    results: [],            // Search results
    showResults: false,     // Whether to display results
}
```

### Template Binding

```xml
<select
    id="partner_type"
    class="form-select form-select-lg"
    t-model="state.partnerType"
    t-on-change="onPartnerTypeChange"
>
    <option value="individual">Individual</option>
    <option value="group">Group</option>
</select>
```

### Results Display

```xml
<td>
    <span t-if="partner.is_group" class="badge bg-info">
        <i class="fa fa-users me-1" /> Group
    </span>
    <span t-else="" class="badge bg-success">
        <i class="fa fa-user me-1" /> Individual
    </span>
</td>
```

## Future Enhancements

Possible improvements:
1. ~~Add partner type filter~~ ✅ DONE
2. ~~Add is_registrant filter~~ ✅ DONE
3. Add multiple field search (AND/OR conditions)
4. Add saved search templates
5. Add advanced filters sidebar
6. Add bulk actions on results

## Support

For issues or questions about this feature:
1. Check `TROUBLESHOOTING.md`
2. Review test file for usage examples
3. Contact OpenSPP development team

---

**Enhancement Date:** October 30, 2025  
**Module Version:** 17.0.1.3.0  
**Status:** ✅ Complete and Tested

