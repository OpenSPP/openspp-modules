# Wizard Integration - Dynamic Event Types

## Overview

This document explains how dynamically created event types are automatically integrated with the OpenSPP event
creation wizard.

## Problem Solved

Previously, dynamically created event types from YAML specifications were not appearing in the event creation
wizard dropdown. This made them unusable in the UI, even though the models were successfully created.

## Solution Implemented

### 1. Dynamic Selection Field

Created an inherited wizard (`wizard/create_event_wizard.py`) that:

- **Dynamically populates** the `event_data_model` selection field
- **Queries** `spp.event.type.definition` for all deployed event types
- **Validates** that the model exists before adding it to the selection
- **Updates automatically** when new event types are deployed

```python
@api.model
def _get_event_data_model_selection(self):
    """Dynamically get event types from deployed event type definitions"""
    selection = [("default", "None")]

    event_type_defs = self.env["spp.event.type.definition"].search([
        ("state", "=", "deployed"),
        ("model_deployed", "=", True),
    ])

    for event_type in event_type_defs:
        model_name = event_type.technical_name
        model_exists = self.env["ir.model"].search([("model", "=", model_name)], limit=1)
        if model_exists:
            selection.append((model_name, event_type.name))

    return selection
```

### 2. Generic Event Wizard

Created a generic wizard (`wizard/create_dynamic_event_wizard.py`) that:

- **Handles all dynamically created event types** without needing specific wizard classes
- **Provides standard fields**: name, summary, description
- **Creates event records** for any dynamic model
- **Links to spp.event.data** framework automatically

### 3. Wizard Flow Override

Extended the `next_page()` method to:

- **Detect dynamic event types** by checking `spp.event.type.definition`
- **Route to generic wizard** for dynamic models
- **Preserve default behavior** for static models (from spp_event_demo)

```python
def next_page(self):
    """Override to handle dynamic event types"""
    if self.event_data_model and not self.event_data_model == "default":
        event_type_def = self.env["spp.event.type.definition"].search([
            ("technical_name", "=", self.event_data_model),
            ("state", "=", "deployed"),
        ], limit=1)

        if event_type_def:
            # Use generic wizard for dynamic models
            # ...create event_data and show generic wizard...
        else:
            # Use default behavior for static models
            return super().next_page()
```

## How It Works

### Deployment Flow

```
1. User creates YAML specification
   ↓
2. Deploy event types
   ↓
3. Models created with ir.model
   ↓
4. Event type marked as deployed
   ↓
5. AUTOMATIC: Event type appears in wizard dropdown
   ↓
6. User selects event type in wizard
   ↓
7. Generic wizard opens with standard fields
   ↓
8. User fills in details and creates event
   ↓
9. Event record created and linked to registrant
```

### User Experience

**Before Fix:**

- ❌ Deploy YAML → models created
- ❌ Open event wizard → new types not in dropdown
- ❌ Cannot use dynamically created types

**After Fix:**

- ✅ Deploy YAML → models created
- ✅ Open event wizard → new types appear immediately
- ✅ Select dynamic type → generic wizard opens
- ✅ Fill in details → event created successfully

## Files Created/Modified

### New Files:

1. **`wizard/create_event_wizard.py`**

   - Inherits `spp.create.event.wizard`
   - Dynamic selection field
   - Override `next_page()` method

2. **`wizard/create_dynamic_event_wizard.py`**

   - Generic wizard model for all dynamic event types
   - Standard fields (name, summary, description)
   - `create_event()` method

3. **`wizard/create_dynamic_event_wizard.xml`**
   - Form view for generic wizard
   - Simple, clean interface

### Modified Files:

1. **`wizard/__init__.py`**

   - Added imports for new wizard models

2. **`__manifest__.py`**

   - Added wizard XML to data files

3. **`security/ir.model.access.csv`**

   - Added access rights for wizard model

4. **`models/event_type_definition.py`**
   - Updated `_register_event_type()` method documentation

## Usage Example

### Step 1: Deploy Event Type from YAML

```yaml
event_types:
  - id: "farmer_assessment"
    name: "Farmer Assessment"
    model: "spp.event.farmer.assessment"
    fields:
      - name: "farm_size"
        label: "Farm Size (hectares)"
        field_type: "float"
      - name: "crop_type"
        label: "Crop Type"
        field_type: "char"
```

Click **Deploy Event Types**

### Step 2: Create Event

1. Open registrant form
2. Click **Event Data** button
3. In wizard, **Event Type** dropdown now shows:
   - None
   - House Visit (from spp_event_demo)
   - Phone Survey (from spp_event_demo)
   - **Farmer Assessment** ← NEW! Dynamic type
4. Select "Farmer Assessment"
5. Click **Next**
6. Generic wizard opens with:
   - Name
   - Summary
   - Description
7. Fill in details
8. Click **Create Event**
9. Event created and linked to registrant ✓

## Benefits

### For Users:

- ✅ **Seamless integration** - deployed types immediately available
- ✅ **No manual configuration** - fully automatic
- ✅ **Consistent experience** - same workflow as static types
- ✅ **Simple interface** - generic wizard for all dynamic types

### For Developers:

- ✅ **No code changes** needed for new event types
- ✅ **Automatic registration** via selection field
- ✅ **Single wizard** handles all dynamic types
- ✅ **Maintainable** - one place to update wizard logic

### For System:

- ✅ **Dynamic** - no module restart required
- ✅ **Scalable** - handles unlimited event types
- ✅ **Clean** - no database hacks or workarounds
- ✅ **Standard** - uses Odoo patterns and conventions

## Technical Details

### Why Dynamic Selection?

Odoo selection fields are normally static (defined at class definition). We overcome this by:

1. Using a **method** instead of a list: `selection="_get_event_data_model_selection"`
2. Method is called **every time** the field is accessed
3. Queries database for **current deployed types**
4. Returns **up-to-date selection** list

### Why Generic Wizard?

Creating specific wizards for each dynamic event type would require:

- Dynamically creating transient model classes
- Dynamically creating view XML
- Complex metaclass manipulation
- Risk of memory leaks

Instead, we use a **single generic wizard** that:

- Works for all dynamic event types
- Provides standard fields
- Can be extended if needed
- Simple and maintainable

### Compatibility with Static Event Types

The solution preserves backward compatibility:

- **Static types** (from spp_event_demo): Use original wizard flow
- **Dynamic types** (from spec loader): Use generic wizard
- **Both work together** in the same dropdown
- **No conflicts** - detection is automatic

## Future Enhancements

Potential improvements:

1. **Dynamic Field Generation**

   - Generate wizard fields from event type definition
   - Show custom fields in wizard UI
   - Use field definitions from YAML

2. **Custom Wizard Views**

   - Allow YAML to specify wizard layout
   - Generate custom views per event type
   - More complex field arrangements

3. **Field Validation**

   - Apply field constraints from YAML
   - Required fields enforcement
   - Data type validation

4. **Wizard Templates**
   - Pre-built wizard templates for common patterns
   - Assessment template
   - Visit template
   - Survey template

## Troubleshooting

### Event type not appearing in dropdown

**Check:**

1. Event type is deployed: `state = 'deployed'`
2. Model is created: `model_deployed = True`
3. Model exists in `ir.model`
4. Technical name is correct

**Debug:**

```python
# In Odoo shell
event_types = env["spp.event.type.definition"].search([
    ("state", "=", "deployed"),
    ("model_deployed", "=", True),
])
for et in event_types:
    print(f"{et.name}: {et.technical_name}")
```

### Generic wizard not opening

**Check:**

1. View exists: `view_spp_create_dynamic_event_wizard_form`
2. Security access granted for user group
3. Event data record created successfully

### Event record not created

**Check:**

1. Model name is correct (starts with `x_`)
2. Required fields have values
3. Field names match model definition
4. User has permission to create records

## Support

For issues or questions:

- GitHub Issues: https://github.com/OpenSPP/openspp-modules/issues
- Documentation: OpenSPP docs
- Community: OpenSPP Slack/Discord

---

**Version**: 17.0.1.0.3
**Date**: November 2024
**Status**: ✅ Implemented and Tested
