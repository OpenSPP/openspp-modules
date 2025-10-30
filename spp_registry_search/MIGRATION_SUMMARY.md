# Migration Summary: spp_base_common → spp_registry_search

**Date:** October 30, 2025  
**From Module:** `spp_base_common`  
**To Module:** `spp_registry_search`  
**Module Version:** 17.0.1.0.0

## Overview

All registry search functionality has been extracted from `spp_base_common` into a new dedicated module `spp_registry_search`. This provides better modularity and allows installations to optionally include advanced search features.

## What Was Moved

### Models
- `partner_search_field.py` - Configuration model for searchable fields
- `res_partner.py` - Extended with search methods (search_by_field, get_searchable_fields)

### Views
- `partner_search_field_view.xml` - Admin configuration interface
- `partner_custom_search_view.xml` - User search interface

### Data
- `partner_search_field_data.xml` - Default searchable field configurations

### JavaScript/Templates
- `static/src/js/partner_search_view.js` - Main search component
- `static/src/js/partner_search_widget.js` - Alternative widget
- `static/src/xml/partner_search_view.xml` - Main template
- `static/src/xml/partner_search_widget.xml` - Widget template

### Tests
- `test_partner_search.py` - Comprehensive test suite (11 tests)

### Documentation
- `PARTNER_TYPE_FILTER.md`
- `TARGET_TYPE_FEATURE.md`
- `TROUBLESHOOTING.md`
- `QUICK_REFERENCE.md`
- `IMPLEMENTATION_SUMMARY.md`
- `MODULE_STRUCTURE.txt`

### Security
- Access rules for `spp.partner.search.field` model

## Changes Made

### New Module: spp_registry_search

**Created Files:**
1. `__manifest__.py` - Module manifest
2. `__init__.py` - Module entry point
3. `README.rst` - Module documentation
4. `pyproject.toml` - Build configuration
5. `models/__init__.py` - Models package init
6. `tests/__init__.py` - Tests package init
7. `security/ir.model.access.csv` - Security rules

**Updated References:**
- Changed all template names from `spp_base_common.*` to `spp_registry_search.*`
- Updated menu names to "Registry Search" terminology
- Updated help text to reference "registry" instead of "partner"

### Updated Module: spp_base_common

**Removed Files:**
- All search-related models, views, data, static files, tests, and documentation

**Updated Files:**
1. `__manifest__.py`:
   - Removed search-related data files
   - Removed search-related assets
   
2. `models/__init__.py`:
   - Removed `partner_search_field` import
   
3. `models/res_partner.py`:
   - Removed `search_by_field()` method
   - Removed `get_searchable_fields()` method
   - Restored to original state
   
4. `tests/__init__.py`:
   - Removed `test_partner_search` import
   
5. `security/ir.model.access.csv`:
   - Removed all `spp_partner_search_field` access rules

## Installation Instructions

### For New Installations

Install the new module:
```bash
odoo-bin -i spp_registry_search -d your_database
```

### For Existing Installations

1. **First, uninstall the old module's search data** (if upgrading from old spp_base_common):
   ```bash
   # This step may require manual cleanup in the database
   # if search data was already installed
   ```

2. **Upgrade spp_base_common** to remove search functionality:
   ```bash
   odoo-bin -u spp_base_common -d your_database
   ```

3. **Install the new search module**:
   ```bash
   odoo-bin -i spp_registry_search -d your_database
   ```

4. **Verify** the installation:
   - Go to Registry → Registry Search
   - Check Settings → Administration → Registry Search Fields

## Dependencies

### spp_registry_search depends on:
- `base`
- `g2p_registry_base`

### Modules that should depend on spp_registry_search:
Any module that wants to use the advanced registry search functionality should add:
```python
"depends": [
    ...,
    "spp_registry_search",
],
```

## Features

The new `spp_registry_search` module provides:

1. **Configurable Search Fields**: Admins can configure which fields are searchable
2. **Dynamic Field Filtering**: Fields filter by registrant type (Individual/Group)
3. **Target Type Support**: Fields can be Individual, Group, or Both
4. **Intuitive Search Interface**: Full-width, modern UI
5. **Type-Aware Search**: Different strategies for different field types
6. **Always Filters Registrants**: Automatically filters by is_registrant=True

## Menu Locations

### For Users:
**Registry → Registry Search**

### For Administrators:
**Settings → Administration → Registry Search Fields**

## API Compatibility

The API remains the same. Code using the search functionality will continue to work:

```python
# Get searchable fields
fields = env['res.partner'].get_searchable_fields('individual')

# Search by field
results = env['res.partner'].search_by_field('name', 'John', is_group=False)
```

## Testing

Run tests for the new module:
```bash
odoo-bin -u spp_registry_search --test-enable --stop-after-init -d your_database
```

## Rollback Plan

If issues occur, you can:
1. Uninstall `spp_registry_search`
2. Restore old `spp_base_common` from backup
3. Upgrade/reinstall `spp_base_common`

## Benefits of Separation

1. **Modularity**: Search functionality can be optionally installed
2. **Maintainability**: Easier to maintain and update search features
3. **Performance**: Systems not using search don't load unnecessary code
4. **Clarity**: Clear separation of concerns
5. **Flexibility**: Other modules can depend on search without pulling in all of spp_base_common

## Notes

- All functionality remains the same
- No data loss (search configurations can be migrated)
- Backward compatible API
- Same security model
- Same user experience

## Support

For issues or questions:
- Check `README.rst` in the spp_registry_search module
- Review test examples
- Contact OpenSPP development team

---

**Migration Status:** ✅ Complete  
**Tested:** ✅ Yes  
**Ready for Production:** ✅ Yes

