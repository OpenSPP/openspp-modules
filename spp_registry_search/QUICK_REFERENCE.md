# Partner Custom Search - Quick Reference Card

## 🚀 Installation

```bash
# Upgrade the module
odoo-bin -u spp_base_common -d your_database

# Run tests
odoo-bin -u spp_base_common --test-enable --stop-after-init -d your_database
```

## 📍 Menu Locations

### For Users:
**Registry → Partner Search**  
Beautiful search interface with dropdown field selector

### For Administrators:
**Settings → Administration → Partner Search Fields**  
Configure which fields are searchable

## 🔧 Quick Configuration (Admin)

1. Go to Settings → Administration → Partner Search Fields
2. Click "Create"
3. Fill in:
   - **Field Label**: "Custom Field Name"
   - **Field**: Select from partner fields
   - **Sequence**: Number (lower = appears first)
   - **Active**: Check to enable
4. Click "Save"

## 🔍 Quick Search (User)

1. Go to Registry → Partner Search
2. Select partner type (Individual or Group)
3. Select field from dropdown
4. Type search value
5. Press Enter or click Search
6. Click "Open" on any result

## 📝 Pre-Configured Fields (Active by Default)

- ✅ Name
- ✅ Email
- ✅ Phone
- ✅ Mobile
- ✅ Reference
- ✅ Tax ID

## 💻 Python API

```python
# Get searchable fields
fields = self.env['res.partner'].get_searchable_fields()
# Returns: [{'id': 1, 'name': 'Name', 'field_name': 'name', 'field_type': 'char'}, ...]

# Search partners by field
partners = self.env['res.partner'].search_by_field('name', 'John', is_group=False)
# Returns: list of matching partner IDs
# Note: Always filters by is_registrant=True

# Search for groups
groups = self.env['res.partner'].search_by_field('name', 'Smith Family', is_group=True)

# Create search field config
search_field = self.env['spp.partner.search.field'].create({
    'name': 'City',
    'field_id': self.env.ref('base.field_res_partner__city').id,
    'sequence': 100,
    'active': True,
})
```

## 🌐 JavaScript API

```javascript
// Get searchable fields
const fields = await this.orm.call(
    'res.partner',
    'get_searchable_fields',
    []
);

// Search individuals
const individuals = await this.orm.call(
    'res.partner',
    'search_by_field',
    ['name', 'John', false]  // false = is_group
);

// Search groups
const groups = await this.orm.call(
    'res.partner',
    'search_by_field',
    ['name', 'Smith Family', true]  // true = is_group
);
```

## 🔐 Security Groups

| Group | Access |
|-------|--------|
| `read_registry` | Read search configs |
| `write_registry` | Edit search configs |
| `create_registry` | Create search configs |
| `base.group_system` | Full admin access |

## 🎨 Field Type Support

| Type | Search Behavior | Example |
|------|----------------|---------|
| Text (char/text) | Partial, case-insensitive | "john" finds "John Doe" |
| Number (int/float) | Exact match | "42" finds 42 |
| Boolean | True/False | "true" or "false" |
| Selection | Exact value | "active" |
| Many2one | Related record name | "USA" finds country |
| Date | Exact date | "2025-10-30" |

## 📂 Key Files

```
models/
  └── partner_search_field.py       # Configuration model

views/
  ├── partner_search_field_view.xml # Admin interface
  └── partner_custom_search_view.xml # User interface

static/src/
  ├── js/
  │   └── partner_search_view.js    # Main component
  └── xml/
      └── partner_search_view.xml   # Template

tests/
  └── test_partner_search.py        # Test suite

data/
  └── partner_search_field_data.xml # Default fields
```

## 🐛 Troubleshooting

### No results found?
- ✓ Check field is Active
- ✓ Verify search value format
- ✓ Confirm you have partner read access

### Field not in dropdown?
- ✓ Check Active checkbox
- ✓ Verify user permissions
- ✓ Refresh browser

### Can't access configuration?
- ✓ Need write_registry or admin role
- ✓ Contact administrator

## 📚 Full Documentation

- **User Guide**: `readme/PARTNER_SEARCH.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Module Structure**: `MODULE_STRUCTURE.txt`

## 🧪 Test Coverage

10 comprehensive tests covering:
- Configuration CRUD
- Search functionality
- Edge cases
- Security constraints

## ⚡ Performance Tips

1. Keep Active fields to minimum needed
2. Use specific field types when possible
3. Consider indexing frequently searched fields
4. Monitor search patterns

## 🎯 Common Use Cases

### Search Individual by Name
Type: Individual → Field: Name → Value: "John"

### Search Group by Name
Type: Group → Field: Name → Value: "Smith Family"

### Search by Email
Type: Individual → Field: Email → Value: "john@example.com"

### Search by Phone
Type: Individual/Group → Field: Phone → Value: "+1234567890"

### Search by ID/Reference
Type: Individual/Group → Field: Reference → Value: "REF001"

## 📞 Support

Questions? Check the docs or contact OpenSPP team.

---
**Version**: 17.0.1.3.0 | **Status**: ✅ Ready | **Updated**: Oct 30, 2025

