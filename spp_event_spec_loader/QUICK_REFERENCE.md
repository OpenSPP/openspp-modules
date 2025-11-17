# OpenSPP Event Spec Loader - Quick Reference Card

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Install dependencies
pip install pyyaml

# 2. Install module
odoo-bin -d your_db -i spp_event_spec_loader

# 3. Navigate to
Registry → Configuration → Event Spec Loader → Program Specifications

# 4. Create → Upload YAML file (or paste manually) → Validate → Deploy
```

## 📝 Template Files

The module includes template files you can copy and modify:

1. **program_spec_simple_template.yaml** - Quick start (minimal)
2. **program_spec_template.yaml** - Complete reference (all options)

**Location**: Module root directory

**Quick Start Template**:
```yaml
program:
  name: "My Program"
  currency: "USD"

event_types:
  - id: "my_event"
    name: "My Event"
    model: "spp.event.my_event"
    fields:
      - name: "event_date"
        field_type: "date"
      - name: "notes"
        field_type: "text"
```

## 🎯 YAML Sections That Generate Events

| YAML Section | Generates | Example Model Name |
|--------------|-----------|-------------------|
| `external_systems` | Evidence provider events | `spp.event.education.attendance` |
| `compliance.conditions` | Verification events | `spp.event.compliance.edu_attendance` |
| `event_types` | Custom events | `spp.event.house.visit` |

## 🔧 Field Types

| YAML Type | Odoo Type | UI Widget |
|-----------|-----------|-----------|
| `string` | `char` | Text input |
| `text` | `text` | Multi-line |
| `number` | `float` | Number input |
| `boolean` | `boolean` | Checkbox |
| `date` | `date` | Date picker |
| `datetime` | `datetime` | DateTime picker |

## 📍 Common Paths

```
Menu Access:
└── Registry
    └── Configuration
        └── Event Spec Loader
            ├── Program Specifications
            └── Event Type Definitions

Models:
└── spp.program.spec        (Program specifications)
└── spp.event.type.definition (Event type definitions)
└── spp.event.*            (Generated event models)
```

## ⚡ Key Actions

### On Program Spec
- **Validate**: Parse YAML and extract metadata
- **Deploy Event Types**: Create all models/views
- **Reset to Draft**: Allow re-editing
- **View Event Types**: See generated types (smart button)

### On Event Type Definition
- **Deploy**: Create model and views
- **Undeploy**: Remove views (preserves data)

## 🎬 Typical Workflow

```
1. Write YAML specification
   ↓
2. Create Program Spec record
   ↓
3. Paste YAML content
   ↓
4. Click "Validate"
   ↓
5. Review extracted metadata
   ↓
6. Click "Deploy Event Types"
   ↓
7. View created event types (smart button)
   ↓
8. Use in registrant forms
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Invalid YAML | Check indentation, colons, brackets |
| Events not in wizard | Restart Odoo service |
| Views not showing | Clear cache, restart |
| Model already exists | Normal; system updates existing model |

## 📊 Example: From YAML to Models

**Input YAML:**
```yaml
external_systems:
  - id: "DepEd"
    domain: "education"
    data_contract:
      record_type: "attendance"
      required_fields:
        - name: "attendance_pct"
          type: "number"

compliance:
  conditions:
    - id: "edu_attendance"
      description: "≥85% attendance"

event_types:
  - id: "house_visit"
    name: "House Visit"
    model: "spp.event.house.visit"
    fields:
      - name: "is_farm"
        field_type: "boolean"
```

**Generated Models:**
1. ✅ `spp.event.education.attendance`
2. ✅ `spp.event.compliance.edu_attendance`
3. ✅ `spp.event.house.visit`

**Each model gets:**
- ✅ Odoo model (ir.model)
- ✅ Tree view
- ✅ Form view
- ✅ Security rules
- ✅ Integration with spp_event_data

## 💡 Pro Tips

### ✓ DO
- ✅ Use version control for YAML files
- ✅ Test with demo data first
- ✅ Document fields with comments
- ✅ Use clear, namespaced model names
- ✅ Start small, add incrementally

### ✗ DON'T
- ❌ Deploy to production without testing
- ❌ Use tabs for indentation (use spaces)
- ❌ Create 100+ event types at once
- ❌ Forget to backup before major changes
- ❌ Use generic model names like "event"

## 📚 Documentation Files

- `README.rst` - Full documentation
- `USAGE_GUIDE.md` - Step-by-step guide
- `MODULE_SUMMARY.md` - Technical overview
- `QUICK_REFERENCE.md` - This file

## 🔗 Useful Links

- Simple template: `program_spec_simple_template.yaml` (in module root)
- Complete template: `program_spec_template.yaml` (in module root)
- Full example: `4ps_best_practice_example_v7.yaml`
- Tests: `tests/test_*.py`
- GitHub: `github.com/OpenSPP/openspp-modules`

## ⚙️ Security Roles

| Role | Can View | Can Create | Can Deploy |
|------|----------|------------|------------|
| Admin | ✅ | ✅ | ✅ |
| Registrar | ✅ | ❌ | ❌ |
| User | Event data | Event data | ❌ |

## 📞 Support

- Issues: GitHub Issues
- Docs: docs.openspp.org
- Community: OpenSPP Slack

---

**Version**: 17.0.1.0.0 | **License**: LGPL-3 | **Status**: Alpha

