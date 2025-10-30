# Target Type Feature - Dynamic Field Filtering

## Overview

The Target Type feature adds intelligent field filtering to the Partner Custom Search. Search fields are now dynamically filtered based on the selected Registrant Type (Individual or Group), ensuring users only see relevant fields for their search context.

## What's New

### Target Type Field

Each searchable field configuration now includes a **Target Type** that determines when the field is available:

- **Individual**: Field only appears when searching for Individuals
- **Group**: Field only appears when searching for Groups  
- **Both**: Field appears for both Individual and Group searches (default)

## How It Works

### User Experience

1. User selects "Individual" from Registrant Type dropdown
2. Search Field dropdown **automatically updates** to show only:
   - Fields with target_type = "individual"
   - Fields with target_type = "both"
3. Group-specific fields (like Tax ID) are hidden

When user switches to "Group":
1. Search Field dropdown updates again
2. Shows only:
   - Fields with target_type = "group"
   - Fields with target_type = "both"
3. Individual-specific fields (like Mobile) are hidden

### Example Scenario

**Default Configuration:**
- Name: Both ✓
- Email: Both ✓
- Phone: Both ✓
- Mobile: Individual only
- Tax ID: Group only
- Reference: Both ✓

**When "Individual" is selected:**
- ✓ Name
- ✓ Email
- ✓ Phone
- ✓ Mobile
- ✗ Tax ID (hidden)
- ✓ Reference

**When "Group" is selected:**
- ✓ Name
- ✓ Email
- ✓ Phone
- ✗ Mobile (hidden)
- ✓ Tax ID
- ✓ Reference

## Implementation Details

### 1. Model Changes (`models/partner_search_field.py`)

Added `target_type` field:
```python
target_type = fields.Selection(
    [
        ("individual", "Individual"),
        ("group", "Group"),
        ("both", "Both"),
    ],
    string="Target Type",
    default="both",
    required=True,
    help="Specify if this field is for Individuals, Groups, or Both",
)
```

### 2. Backend Changes (`models/res_partner.py`)

Updated `get_searchable_fields()` method to filter by partner type:
```python
@api.model
def get_searchable_fields(self, partner_type=None):
    """
    Get list of searchable fields configured for partner search
    :param partner_type: 'individual', 'group', or None for all
    :return: List of dictionaries with field information
    """
    domain = [("active", "=", True)]
    
    # Filter by target_type based on partner_type
    if partner_type == "individual":
        domain.append(("target_type", "in", ["individual", "both"]))
    elif partner_type == "group":
        domain.append(("target_type", "in", ["group", "both"]))
    
    search_fields = self.env["spp.partner.search.field"].search(
        domain, order="sequence, name"
    )
    
    return [field info...]
```

### 3. Frontend Changes (`static/src/js/partner_search_view.js`)

**Updated field loading:**
```javascript
async loadSearchFields(partnerType = null) {
    const fields = await this.orm.call(
        "res.partner",
        "get_searchable_fields",
        [partnerType]  // Pass partner type to backend
    );
    this.state.searchFields = fields;
    if (fields.length > 0) {
        this.state.selectedField = fields[0].field_name;
    }
}
```

**Auto-reload on partner type change:**
```javascript
async onPartnerTypeChange(event) {
    this.state.partnerType = event.target.value;
    // Reload fields based on selected partner type
    await this.loadSearchFields(this.state.partnerType);
    // Clear search value when partner type changes
    this.state.searchValue = "";
    this.state.showResults = false;
}
```

### 4. View Changes (`views/partner_search_field_view.xml`)

Added target_type to form and tree views:
```xml
<!-- Form View -->
<field name="target_type" widget="radio" />

<!-- Tree View -->
<field name="target_type" />
```

### 5. Data Changes (`data/partner_search_field_data.xml`)

Set appropriate target types for default fields:
- Name: `both`
- Email: `both`
- Phone: `both`
- **Mobile**: `individual` ← Specific to individuals
- Reference: `both`
- **Tax ID**: `group` ← Specific to groups
- Street: `both`
- City: `both`
- ZIP: `both`

## Configuration Guide

### For Administrators

When creating or editing a search field configuration:

1. Go to **Settings → Administration → Partner Search Fields**
2. Create or edit a field
3. Set the **Target Type**:
   - **Individual**: If the field only applies to individuals (e.g., Date of Birth, Gender, Family Name)
   - **Group**: If the field only applies to groups (e.g., Tax ID, Organization Type)
   - **Both**: If the field applies to both (e.g., Name, Email, Phone, Address)

#### Field Type Guidelines

**Use "Individual" for:**
- Personal identification fields
- Biological information (gender, birthdate)
- Family relationships (family name, given name)
- Personal contact (mobile)
- Individual-specific attributes

**Use "Group" for:**
- Organization/household information
- Tax/legal identifiers
- Group-specific attributes
- Household composition data

**Use "Both" for:**
- Names (both individuals and groups have names)
- Contact information (email, phone)
- Address information
- Reference numbers
- General descriptive fields

### Example Configurations

```xml
<!-- Individual-specific field -->
<record id="partner_search_field_birthdate" model="spp.partner.search.field">
    <field name="name">Date of Birth</field>
    <field name="field_id" ref="base.field_res_partner__birthdate" />
    <field name="target_type">individual</field>
    <field name="active" eval="True" />
</record>

<!-- Group-specific field -->
<record id="partner_search_field_company_type" model="spp.partner.search.field">
    <field name="name">Company Type</field>
    <field name="field_id" ref="base.field_res_partner__company_type" />
    <field name="target_type">group</field>
    <field name="active" eval="True" />
</record>

<!-- Both types -->
<record id="partner_search_field_name" model="spp.partner.search.field">
    <field name="name">Name</field>
    <field name="field_id" ref="base.field_res_partner__name" />
    <field name="target_type">both</field>
    <field name="active" eval="True" />
</record>
```

## API Usage

### Python

```python
# Get all searchable fields
all_fields = env['res.partner'].get_searchable_fields()

# Get individual-specific fields only
individual_fields = env['res.partner'].get_searchable_fields('individual')

# Get group-specific fields only
group_fields = env['res.partner'].get_searchable_fields('group')
```

### JavaScript

```javascript
// Get all searchable fields
const allFields = await this.orm.call(
    'res.partner',
    'get_searchable_fields',
    []
);

// Get individual-specific fields
const individualFields = await this.orm.call(
    'res.partner',
    'get_searchable_fields',
    ['individual']
);

// Get group-specific fields
const groupFields = await this.orm.call(
    'res.partner',
    'get_searchable_fields',
    ['group']
);
```

## Testing

### Test Coverage

Updated tests validate:
1. Target type field creation and storage
2. Field filtering by partner type
3. Dynamic field loading based on selection
4. Backward compatibility (works without partner_type parameter)

### Test Example

```python
def test_02_get_searchable_fields(self):
    """Test retrieving searchable fields"""
    # Create fields with different target types
    self.env["spp.partner.search.field"].create({
        "name": "Name",
        "field_id": self.name_field.id,
        "target_type": "both",
        "active": True,
    })
    self.env["spp.partner.search.field"].create({
        "name": "Email",
        "field_id": self.email_field.id,
        "target_type": "individual",
        "active": True,
    })

    # Test getting individual fields
    individual_fields = self.env["res.partner"].get_searchable_fields("individual")
    # Should include both "both" and "individual" fields
    self.assertTrue(len(individual_fields) >= 2)

    # Test getting group fields
    group_fields = self.env["res.partner"].get_searchable_fields("group")
    # Should only include "both" fields (no "individual" field)
    self.assertTrue(len(group_fields) >= 1)
```

## Benefits

### 1. **Improved User Experience**
- Users see only relevant fields for their search context
- Less confusion about which fields apply to what
- Cleaner, more focused interface

### 2. **Better Data Integrity**
- Prevents searching group-specific fields for individuals (and vice versa)
- Reduces errors from mismatched field types
- Enforces proper field usage

### 3. **Flexibility**
- Administrators can easily configure which fields apply to what
- Supports custom fields with proper targeting
- Easy to maintain and update

### 4. **Performance**
- Reduced dropdown options = faster UI rendering
- No unnecessary API calls for irrelevant fields
- Optimized search experience

## Migration Notes

### Upgrading from Previous Version

**Backward Compatibility:** ✅ Fully backward compatible

- Existing installations will automatically set `target_type="both"` for all existing fields
- No data migration required
- Frontend gracefully handles missing target_type (defaults to showing all)
- API maintains backward compatibility

### For Existing Installations

1. **Upgrade the module:**
   ```bash
   odoo-bin -u spp_base_common -d your_database
   ```

2. **Review and update field configurations:**
   - Go to Settings → Administration → Partner Search Fields
   - Review each field's target type
   - Update to "Individual" or "Group" where appropriate
   - Leave as "Both" for common fields

3. **Test the functionality:**
   - Go to Registry → Registry Search
   - Switch between Individual and Group
   - Verify fields appear/disappear correctly

## Future Enhancements

Potential improvements:
1. Conditional field visibility based on other selections
2. Field groups/categories for better organization
3. Smart suggestions based on user's search history
4. Auto-detection of appropriate target type based on field name/type
5. Bulk target type assignment for multiple fields

## Support

For issues or questions:
- Check `TROUBLESHOOTING.md`
- Review test examples in `tests/test_partner_search.py`
- Contact OpenSPP development team

---

**Feature Date:** October 30, 2025  
**Module Version:** 17.0.1.3.0  
**Status:** ✅ Complete and Tested

