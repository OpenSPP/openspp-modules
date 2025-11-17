# YAML Templates Guide

## Available Templates

The `spp_event_spec_loader` module provides three levels of YAML templates to suit different needs:

---

## 1. 🚀 Simple Template (Quick Start)

**File**: `program_spec_simple_template.yaml`

**Best for**: 
- First-time users
- Simple programs with basic event tracking
- Quick prototyping
- Learning the basics

**What's included**:
- ✅ Minimal program metadata
- ✅ One example event type
- ✅ Clear inline comments
- ✅ Quick start guide

**Example event generated**:
```
spp.event.my.first.event
```

**Size**: ~60 lines

**Time to customize**: 5-10 minutes

---

## 2. 📚 Complete Template (Full Reference)

**File**: `program_spec_template.yaml`

**Best for**:
- Production programs
- Programs with multiple event types
- Integration with external systems
- Complex compliance requirements
- Full-featured implementations

**What's included**:
- ✅ All YAML sections with examples
- ✅ Multiple event type examples (4 types)
- ✅ External system integration examples
- ✅ Compliance condition examples
- ✅ Comprehensive documentation
- ✅ Best practices and tips

**Example events generated**:
```
spp.event.education.attendance (from external_systems)
spp.event.health.checkup (from external_systems)
spp.event.compliance.education_attendance (from compliance)
spp.event.compliance.health_checkup (from compliance)
spp.event.house.visit (from event_types)
spp.event.phone.survey (from event_types)
spp.event.grievance (from event_types)
spp.event.training (from event_types)
```

**Size**: ~450 lines

**Time to customize**: 1-2 hours

---

## 3. 🏆 Real-World Example (4Ps Program)

**File**: `4ps_best_practice_example_v7.yaml` (external reference)

**Best for**:
- Understanding a complete production specification
- Learning advanced patterns
- Reference for complex programs
- Best practices demonstration

**What's included**:
- ✅ Complete 4Ps CCT program specification
- ✅ Real-world eligibility rules
- ✅ Entitlement calculations
- ✅ External system integrations
- ✅ Compliance workflows
- ✅ Calendar and scheduling

**Size**: ~376 lines

**Complexity**: Production-ready

---

## Comparison Matrix

| Feature | Simple | Complete | 4Ps Example |
|---------|--------|----------|-------------|
| **Program Metadata** | ✅ Basic | ✅ Full | ✅ Full |
| **Event Types** | 1 example | 4 examples | 7+ types |
| **External Systems** | ❌ | ✅ 2 examples | ✅ 2 systems |
| **Compliance** | ❌ | ✅ 2 conditions | ✅ 3 conditions |
| **Entitlements** | ❌ | ✅ 1 example | ✅ 4 components |
| **Workflows** | ❌ | ✅ Basic | ✅ Complete |
| **Documentation** | ✅ Inline | ✅ Extensive | ✅ Complete |
| **Learning Curve** | Easy | Moderate | Advanced |
| **Customization Time** | 5-10 min | 1-2 hours | Reference only |

---

## How to Choose

### Choose **Simple Template** if:
- ✅ You're new to the module
- ✅ You need basic event tracking only
- ✅ You want to get started quickly
- ✅ You have 1-3 event types
- ✅ You don't need external integrations

### Choose **Complete Template** if:
- ✅ You're building a production system
- ✅ You need multiple event types (4+)
- ✅ You need external system integration
- ✅ You need compliance tracking
- ✅ You want all available features
- ✅ You need a comprehensive reference

### Use **4Ps Example** if:
- ✅ You want to see a real-world implementation
- ✅ You're building a CCT program
- ✅ You need advanced patterns
- ✅ You want to understand best practices
- ✅ You're learning the full specification

---

## Usage Instructions

### Step 1: Choose Your Template

Pick based on your needs (see "How to Choose" above)

### Step 2: Copy the Template

```bash
# Navigate to module directory
cd /path/to/openspp-modules/spp_event_spec_loader/

# Copy the template you want
cp program_spec_simple_template.yaml my_program.yaml
# OR
cp program_spec_template.yaml my_program.yaml
```

### Step 3: Customize

Open `my_program.yaml` in your favorite editor:

```bash
# Use any text editor
code my_program.yaml          # VS Code
nano my_program.yaml          # Nano
vim my_program.yaml           # Vim
```

**Key sections to modify**:
1. `program.name` - Your program name
2. `program.currency` - Your currency code
3. `event_types` - Your event definitions
4. Field names and labels
5. Remove sections you don't need

### Step 4: Validate

Check your YAML syntax:

```bash
# Option 1: Use yamllint
yamllint my_program.yaml

# Option 2: Use Python
python -c "import yaml; yaml.safe_load(open('my_program.yaml'))"

# Option 3: Online validator
# Visit: https://www.yamllint.com/
```

### Step 5: Upload to OpenSPP

1. Open OpenSPP
2. Navigate to: **Registry → Configuration → Event Spec Loader → Program Specifications**
3. Click **Create**
4. Fill in **Name** and **Code**
5. Go to **Upload YAML** tab
6. Click **Choose File** and select `my_program.yaml`
7. Click **Validate**
8. Review extracted metadata
9. Click **Deploy Event Types**
10. Done! ✅

---

## Template Customization Guide

### Minimal Changes (Simple Template)

```yaml
# 1. Change program name
program:
  name: "My Program"  # ← Change this
  
# 2. Modify event type
event_types:
  - id: "my_event"  # ← Change this
    name: "My Event"  # ← Change this
    model: "spp.event.my_event"  # ← Change this
    fields:
      - name: "my_field"  # ← Add your fields
        label: "My Field"
        field_type: "char"
```

### Adding More Event Types

```yaml
event_types:
  # Existing event
  - id: "event_1"
    name: "First Event"
    model: "spp.event.first"
    fields:
      - name: "field1"
        label: "Field 1"
        field_type: "char"
  
  # Add new event (copy structure above)
  - id: "event_2"
    name: "Second Event"
    model: "spp.event.second"
    fields:
      - name: "field2"
        label: "Field 2"
        field_type: "date"
```

### Adding Fields to Event Types

```yaml
fields:
  # Basic text field
  - name: "text_field"
    label: "Text Field"
    field_type: "char"
  
  # Number field
  - name: "number_field"
    label: "Number"
    field_type: "float"
  
  # Date field
  - name: "date_field"
    label: "Date"
    field_type: "date"
  
  # Yes/No field
  - name: "yes_no_field"
    label: "Yes/No"
    field_type: "boolean"
  
  # Long text field
  - name: "notes_field"
    label: "Notes"
    field_type: "text"
```

---

## Common Customization Patterns

### Pattern 1: Assessment Event

```yaml
- id: "assessment"
  name: "Household Assessment"
  model: "spp.event.assessment"
  fields:
    - name: "assessment_date"
      field_type: "date"
    - name: "assessor_name"
      field_type: "char"
    - name: "score"
      field_type: "float"
    - name: "recommendations"
      field_type: "text"
```

### Pattern 2: Visit Event

```yaml
- id: "visit"
  name: "Field Visit"
  model: "spp.event.visit"
  fields:
    - name: "visit_date"
      field_type: "date"
    - name: "visitor_name"
      field_type: "char"
    - name: "location"
      field_type: "char"
    - name: "visited"
      field_type: "boolean"
    - name: "notes"
      field_type: "text"
```

### Pattern 3: Verification Event

```yaml
- id: "verification"
  name: "Data Verification"
  model: "spp.event.verification"
  fields:
    - name: "verification_date"
      field_type: "date"
    - name: "verified_by"
      field_type: "char"
    - name: "verified"
      field_type: "boolean"
    - name: "verification_notes"
      field_type: "text"
```

---

## Tips and Best Practices

### ✅ DO:
1. Start with simple template for learning
2. Use descriptive field names (e.g., `visit_date` not `date1`)
3. Add comments to explain complex logic
4. Test with one event type first
5. Export your spec for backup
6. Keep specs in version control
7. Validate YAML before uploading
8. Use consistent naming conventions

### ❌ DON'T:
1. Don't use spaces in model names (use dots: `spp.event.my.model`)
2. Don't skip the `program` section
3. Don't use special characters in IDs
4. Don't create 50+ event types at once (start small)
5. Don't forget to validate before deploying
6. Don't modify generated models directly
7. Don't use reserved keywords as field names

---

## Troubleshooting

### Error: "Invalid YAML syntax"
**Solution**: Check your indentation (use spaces, not tabs)

### Error: "Model already exists"
**Solution**: This is OK - system updates existing model

### Fields not showing in UI
**Solution**: Clear cache and restart Odoo

### Template seems overwhelming
**Solution**: Start with simple template, ignore other sections

---

## Getting Help

- **Documentation**: See `README.rst` and `USAGE_GUIDE.md`
- **Examples**: See `4ps_best_practice_example_v7.yaml`
- **Issues**: https://github.com/OpenSPP/openspp-modules/issues
- **Community**: OpenSPP Slack/Discord

---

## Template File Locations

All templates are in the module root:

```
openspp-modules/spp_event_spec_loader/
├── program_spec_simple_template.yaml      ← Quick start
├── program_spec_template.yaml             ← Complete reference
├── README.rst                             ← Full documentation
├── USAGE_GUIDE.md                         ← Step-by-step guide
├── QUICK_REFERENCE.md                     ← Cheat sheet
└── TEMPLATES_GUIDE.md                     ← This file
```

---

**Ready to get started?** Pick your template and follow the steps above! 🚀

