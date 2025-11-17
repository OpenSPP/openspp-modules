# OpenSPP Event Spec Loader - Module Summary

## What Was Created

A complete OpenSPP module that dynamically generates event data types and their required components from YAML program specifications. This is a **meta-module** that automates the creation of event tracking infrastructure.

## Module Location

```
/Users/michaelgonzales/ACN/openspp-modules/spp_event_spec_loader/
```

## Core Capabilities

### 1. YAML Program Specification Management

**Model**: `spp.program.spec`

- Stores and validates YAML program specifications
- Extracts program metadata (name, objectives, agencies, currency, languages)
- Parses and validates YAML syntax
- Manages deployment workflow (Draft → Validated → Deployed)
- Tracks deployment history and errors

**Key Features**:
- Built-in YAML editor with syntax highlighting
- Automatic metadata extraction
- JSON preview of parsed data
- Error reporting and validation
- Bulk event type generation

### 2. Event Type Definition Management

**Model**: `spp.event.type.definition`

- Represents individual event types extracted from specifications
- Stores field definitions as JSON
- Tracks deployment status (model, views, wizard)
- Manages event type lifecycle

**Key Features**:
- Auto-generation of technical names
- Field definition storage and validation
- Dynamic model creation
- Dynamic view generation (tree/form)
- Deployment/undeployment controls

### 3. Dynamic Event Type Generation

The module automatically creates event types from three sources:

#### A. External Systems (Evidence Providers)

From `external_systems` section in YAML:
```yaml
external_systems:
  - id: "DepEd"
    domain: "education"
    data_contract:
      record_type: "attendance"
      required_fields:
        - name: "attendance_pct"
          type: "number"
```

**Generates**: `spp.event.education.attendance` with attendance_pct field

#### B. Compliance Conditions

From `compliance.conditions` section:
```yaml
compliance:
  conditions:
    - id: "edu_attendance"
      description: "Child has ≥85% attendance"
```

**Generates**: `spp.event.compliance.edu_attendance` with verification fields

#### C. Custom Event Types

From `event_types` section:
```yaml
event_types:
  - id: "house_visit"
    name: "House Visit"
    model: "spp.event.house.visit"
    fields:
      - name: "is_farm"
        field_type: "boolean"
```

**Generates**: `spp.event.house.visit` with custom fields

### 4. Automated Component Creation

For each event type, the module creates:

1. **Odoo Model** (`ir.model`)
   - Dynamic model with custom fields
   - Standard fields: name, summary, description
   - Custom fields based on YAML definition

2. **Tree View** (`ir.ui.view`)
   - List view with key fields
   - Sortable and searchable

3. **Form View** (`ir.ui.view`)
   - Organized field layout
   - Grouped by related fields

4. **Window Action** (ready for menu integration)

5. **Security Rules** (inherits from parent module)

## File Structure

```
spp_event_spec_loader/
├── __init__.py                      # Module entry point
├── __manifest__.py                  # Module manifest
├── pyproject.toml                   # Build configuration
├── README.rst                       # Full documentation
├── USAGE_GUIDE.md                   # User guide
├── MODULE_SUMMARY.md                # This file
│
├── models/                          # Business logic
│   ├── __init__.py
│   ├── program_spec.py              # YAML spec management
│   ├── event_type_definition.py    # Event type definitions
│   ├── dynamic_event_model.py       # Mixin for dynamic models
│   └── registrant.py                # res.partner extensions
│
├── views/                           # User interface
│   ├── program_spec_view.xml        # Program spec views
│   ├── event_type_definition_view.xml # Event type views
│   └── menu_views.xml               # Menu structure
│
├── wizard/                          # Wizards (extensible)
│   └── __init__.py
│
├── security/                        # Access control
│   └── ir.model.access.csv          # Model permissions
│
├── data/                            # Data files
│   └── demo_program_spec.xml        # Demo 4Ps specification
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_program_spec.py         # Program spec tests
│   └── test_event_type_definition.py # Event type tests
│
├── readme/                          # Documentation fragments
│   └── DESCRIPTION.rst
│
└── static/                          # Static assets
    └── description/                 # Module icon location
```

## How It Works

### Process Flow

```
1. User uploads/pastes YAML specification
   ↓
2. Module parses YAML and validates syntax
   ↓
3. User clicks "Validate" button
   ↓
4. Module extracts metadata and event type definitions
   ↓
5. User clicks "Deploy Event Types" button
   ↓
6. Module creates:
   - Event type definitions
   - Dynamic models (ir.model)
   - Fields (ir.model.fields)
   - Views (ir.ui.view)
   ↓
7. Event types are available for use
```

### Technical Implementation

#### Dynamic Model Creation

Uses Odoo's `ir.model` infrastructure:

```python
model_vals = {
    "name": "House Visit",
    "model": "spp.event.house.visit",
    "state": "manual",
    "field_id": [
        (0, 0, {
            "name": "x_is_farm",
            "field_description": "Is Farm",
            "ttype": "boolean",
            "state": "manual",
        }),
        # More fields...
    ]
}
self.env["ir.model"].create(model_vals)
```

#### View Generation

Dynamically builds XML views:

```python
form_xml = f"""<?xml version="1.0"?>
<form string="{self.name}">
    <sheet>
        <group>
            <field name="x_summary"/>
            {custom_fields_xml}
        </group>
    </sheet>
</form>"""

self.env["ir.ui.view"].create({
    "name": view_name,
    "model": self.technical_name,
    "arch": form_xml,
})
```

## Integration with Existing Modules

### Dependencies

- **spp_event_data**: Core event tracking framework
- **spp_base_common**: OpenSPP utilities
- **base**: Odoo base
- **pyyaml**: YAML parsing library

### Works With

- **spp_event_demo**: Generated types work alongside demo types
- **g2p_registry_base**: Security groups and base models
- **g2p_registry_individual**: Individual registrant forms
- **g2p_registry_group**: Group registrant forms

## Example: 4Ps Program

The included demo specification (`data/demo_program_spec.xml`) generates:

### From External Systems
1. `spp.event.education.attendance` (DepEd integration)
2. `spp.event.health.health_check` (DOH integration)

### From Compliance Conditions
3. `spp.event.compliance.edu_attendance`
4. `spp.event.compliance.health_comp`
5. `spp.event.compliance.fds_attendance`

### From Custom Event Types
6. `spp.event.house.visit.4ps`
7. `spp.event.grievance.4ps`

**Total**: 7 event types created automatically from one YAML file!

## Use Cases

### 1. Rapid Program Deployment

**Scenario**: New CCT program needs event tracking

**Without this module**:
- Manually create 10+ model files
- Write view XML for each (20+ files)
- Create wizard files
- Add security rules
- Write tests
- **Time**: 2-3 weeks

**With this module**:
- Write YAML specification
- Upload and deploy
- **Time**: 2-3 hours

### 2. Program Modifications

**Scenario**: Add new compliance condition

**Without this module**:
- Create new model file
- Add views
- Update wizards
- Deploy module update
- **Time**: 1-2 days

**With this module**:
- Add condition to YAML
- Redeploy specification
- **Time**: 10 minutes

### 3. Multi-Program Management

**Scenario**: Organization manages 5 programs

**Without this module**:
- Maintain 5 separate modules
- Complex dependency management
- Version conflicts

**With this module**:
- 5 YAML specifications
- One module manages all
- Clean separation

## Benefits

### For Developers

✅ **Rapid Development**: Generate models in minutes, not days
✅ **Less Code**: No need to write repetitive model/view files
✅ **Easy Maintenance**: Update YAML instead of Python code
✅ **Version Control**: YAML specs are easy to diff and merge
✅ **Documentation**: YAML serves as living documentation

### For Implementers

✅ **Flexibility**: Adapt to program changes quickly
✅ **Standardization**: Consistent event type structure
✅ **Scalability**: Manage multiple programs easily
✅ **Auditability**: Full deployment history tracking

### For Program Managers

✅ **Speed**: Deploy new programs faster
✅ **Cost**: Reduce development time and cost
✅ **Agility**: Respond to policy changes quickly
✅ **Visibility**: See all event types in one place

## Limitations and Considerations

### Current Limitations

1. **Module Restart Required**: Some features need restart (wizard selections)
2. **Simple Field Types Only**: Complex relations require manual coding
3. **Basic Views**: Generated views are functional but may need customization
4. **No Wizard Generation**: Wizard models not fully automated yet
5. **Performance**: Large numbers of dynamic models may impact performance

### Recommended Limits

- **Event Types per Program**: 10-20
- **Fields per Event Type**: 10-15
- **Total Dynamic Models**: 50-100

### When NOT to Use This Module

❌ Complex event types withMany2one/One2many relationships
❌ Event types needing heavy customization
❌ Performance-critical applications with hundreds of models
❌ When you need full control over every aspect

## Future Enhancements

Potential improvements:

1. **Wizard Generation**: Full automation of wizard models
2. **Menu Generation**: Automatic menu creation
3. **Report Templates**: Generate default reports
4. **Data Migration**: Tools to migrate between event type versions
5. **Version Management**: Track spec versions and rollback
6. **Visual Editor**: GUI for building YAML specs
7. **Import/Export**: Bulk import/export of event types
8. **Template Library**: Pre-built templates for common programs

## Testing

Comprehensive test suite included:

- **test_program_spec.py**: Tests YAML parsing, validation, deployment
- **test_event_type_definition.py**: Tests event type creation, views, fields

Run tests:
```bash
odoo-bin -d test_db --test-tags=spp_event_spec_loader --stop-after-init
```

## Installation

### Prerequisites

```bash
pip install pyyaml
```

### Install Module

```bash
# Via command line
odoo-bin -d your_db -i spp_event_spec_loader

# Via UI
Apps → Search "Event Spec Loader" → Install
```

### With Demo Data

```bash
odoo-bin -d your_db -i spp_event_spec_loader --load-demo
```

## Quick Start

1. **Navigate to**: Registry → Configuration → Event Spec Loader → Program Specifications
2. **Create** new specification
3. **Paste** YAML content (or use demo)
4. Click **Validate**
5. Click **Deploy Event Types**
6. View created types via smart button
7. **Use** event types in registrant forms

## Documentation

- **README.rst**: Full module documentation
- **USAGE_GUIDE.md**: Step-by-step usage instructions
- **MODULE_SUMMARY.md**: This file (technical overview)
- **QUICK_REFERENCE.md**: One-page cheat sheet

## Templates

- **program_spec_simple_template.yaml**: Quick start template (minimal)
- **program_spec_template.yaml**: Complete template (all options)
- **4ps_best_practice_example_v7.yaml**: Real-world example (4Ps program)

## Support

- **GitHub Issues**: https://github.com/OpenSPP/openspp-modules/issues
- **Documentation**: https://docs.openspp.org
- **Community**: OpenSPP Slack/Discord

## Credits

**Authors**: OpenSPP.org  
**Maintainers**: jeremi, gonzalesedwin1123, emjay0921  
**License**: LGPL-3  
**Version**: 17.0.1.0.0  
**Status**: Alpha

## Conclusion

The `spp_event_spec_loader` module represents a significant advancement in OpenSPP's event tracking capabilities. By treating YAML program specifications as the source of truth, it enables rapid, consistent, and maintainable deployment of event tracking infrastructure for social protection programs.

**Key Takeaway**: What previously took weeks of development can now be accomplished in hours through configuration.

