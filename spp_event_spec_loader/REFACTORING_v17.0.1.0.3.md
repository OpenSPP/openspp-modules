# Architectural Refactoring - Version 17.0.1.0.3

## Overview

This document describes the major architectural refactoring implemented to improve the event type registration
system across the OpenSPP event modules.

## Problem Statement

The initial implementation had the dynamic selection logic embedded in `spp_event_spec_loader`, which created
tight coupling and made it difficult for other modules to add event types. Specifically:

1. **Tight Coupling**: Selection logic was in `spp_event_spec_loader` but needed by base module
2. **Hard to Extend**: Other modules couldn't easily add event types to the wizard
3. **Inconsistent Approach**: Different modules used different methods to register event types
4. **Querying Specific Tables**: Logic queried `spp.event.type.definition` which is specific to one module

## Solution: Flag-Based Architecture

We refactored to use a **flag-based architecture** where event models are marked with a boolean field on
`ir.model`.

### Key Principle

> **Any module can mark its models as event types by setting `is_event_model = True` on the `ir.model`
> record**

This creates a:

- ✅ **Decoupled** system - base module handles selection
- ✅ **Extensible** system - any module can add event types
- ✅ **Consistent** system - one standard way to register
- ✅ **Scalable** system - no specific table queries

## Changes Made

### 1. spp_event_data (Base Module)

#### Added: `models/ir_model.py`

```python
class IrModel(models.Model):
    _inherit = "ir.model"

    is_event_model = fields.Boolean(
        string="Is Event Model",
        default=False,
        help="Indicates if this model represents an event type",
    )
```

**Purpose**: Provides the flag that identifies event models.

#### Modified: `wizard/create_event_wizard.py`

**Before**:

```python
event_data_model = fields.Selection(
    [("default", "None")],
    "Event Type",
    default="default",
)
```

**After**:

```python
@api.model
def _get_event_data_model_selection(self):
    """Dynamically get event types from models marked as event models"""
    selection = [("default", "None")]

    # Query all models marked as event models
    event_models = self.env["ir.model"].search(
        [("is_event_model", "=", True)], order="name"
    )

    for event_model in event_models:
        selection.append((event_model.model, event_model.name))

    return selection

event_data_model = fields.Selection(
    selection="_get_event_data_model_selection",
    string="Event Type",
    default="default",
)
```

**Purpose**: Dynamically populates wizard dropdown from flagged models.

**Also Added**: Wizard detection logic to use generic wizard when specific wizard doesn't exist:

```python
# Check if specific wizard exists
wizard_exists = wizard_model in self.env

if not wizard_exists:
    # Try to find a generic wizard (for dynamic models)
    generic_wizard = "%s.create.dynamic.event.wizard" % wizard_list[0]
    if generic_wizard in self.env:
        wizard_model = generic_wizard
```

**Purpose**: Allows dynamic models from `spp_event_spec_loader` to use a generic wizard.

### 2. spp_event_demo

#### Modified: All Event Models

Added `_register_hook` to each model:

```python
@api.model
def _register_hook(self):
    """Mark this model as an event model"""
    super()._register_hook()
    ir_model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)
    if ir_model and not ir_model.is_event_model:
        ir_model.sudo().write({"is_event_model": True})
```

**Files Modified**:

- `models/house_visit.py`
- `models/phone_survey.py`
- `models/school_enrolment.py`

**Purpose**: Automatically marks programmatically defined event models as event types.

### 3. spp_event_spec_loader

#### Modified: `models/event_type_definition.py`

**In `_deploy_model()` method**:

```python
# When creating new model
model_vals = {
    "name": self.name,
    "model": model_name,
    "state": "manual",
    "is_event_model": True,  # Mark as event model
    "field_id": [],
}

# When updating existing model
if existing_model:
    _logger.info("Model %s already exists, updating...", model_name)
    # Ensure existing model is marked as event model
    if not existing_model.is_event_model:
        existing_model.sudo().write({"is_event_model": True})
```

**Purpose**: Ensures all dynamically created models are marked as event types.

#### Removed: `wizard/create_event_wizard.py`

The inheritance of `spp.create.event.wizard` was removed since the logic is now in the base module.

#### Kept: `wizard/create_dynamic_event_wizard.py`

The generic wizard remains as it's still needed to handle dynamic models without specific wizards.

## Architecture Diagram

### Before Refactoring

```
┌─────────────────────────────────────────────────┐
│           spp_event_spec_loader                 │
│  ┌──────────────────────────────────────────┐   │
│  │  create_event_wizard.py (inheritance)    │   │
│  │  - Query spp.event.type.definition       │   │
│  │  - Dynamic selection logic               │   │
│  └──────────────────────────────────────────┘   │
│                   ▲                             │
│                   │ Depends on                  │
└───────────────────┼─────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────┐
│                   │    spp_event_data           │
│  ┌────────────────┴──────────────────────────┐  │
│  │  create_event_wizard.py (base)           │  │
│  │  - Static selection [("default", "None")]│  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Problem**: Derived module controls base behavior ❌

### After Refactoring

```
┌─────────────────────────────────────────────────┐
│              spp_event_data (base)              │
│  ┌──────────────────────────────────────────┐   │
│  │  ir_model.py                             │   │
│  │  + is_event_model: Boolean               │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  create_event_wizard.py                  │   │
│  │  - Query ir.model.is_event_model         │   │
│  │  - Dynamic selection logic               │   │
│  │  - Generic wizard detection              │   │
│  └──────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────┘
                 │ Inherited by
         ┌───────┴────────┐
         │                │
┌────────▼────────┐  ┌────▼────────────────────┐
│ spp_event_demo  │  │ spp_event_spec_loader  │
│                 │  │                        │
│ Set flag:       │  │ Set flag:              │
│ is_event_model  │  │ is_event_model = True  │
│ = True          │  │ (on dynamic models)    │
│                 │  │                        │
│ ✓ house_visit   │  │ ✓ Dynamic models       │
│ ✓ phone_survey  │  │ ✓ Generic wizard       │
│ ✓ school_enrol  │  │                        │
└─────────────────┘  └────────────────────────┘
```

**Benefit**: Base module controls behavior, others just set flag ✅

## Benefits

### 1. Separation of Concerns

- **Base module** (`spp_event_data`): Handles wizard logic
- **Derived modules**: Just mark their models
- **Clean boundaries**: Each module has clear responsibilities

### 2. Extensibility

Any module can now add event types by:

```python
# In your custom module
class MyEventModel(models.Model):
    _name = "custom.event.model"

    @api.model
    def _register_hook(self):
        super()._register_hook()
        ir_model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)
        if ir_model:
            ir_model.sudo().write({"is_event_model": True})
```

No need to inherit wizards or modify other modules!

### 3. Maintainability

- **Single source of truth**: `ir.model.is_event_model`
- **Consistent pattern**: All modules use the same approach
- **Less code**: No duplicate selection logic
- **Easier debugging**: One place to check wizard selection

### 4. Scalability

- **No table coupling**: Doesn't depend on specific module tables
- **Performance**: Simple boolean query on indexed table
- **Future-proof**: Easy to add new event modules

### 5. Backward Compatibility

- ✅ Existing modules work without changes (with update)
- ✅ Existing data preserved
- ✅ No breaking changes to API
- ✅ Graceful fallback for missing wizards

## Migration Guide

### For Existing Installations

1. **Upgrade modules in order**:

   ```bash
   # First upgrade base module
   odoo-bin -d your_db -u spp_event_data

   # Then upgrade demo module
   odoo-bin -d your_db -u spp_event_demo

   # Finally upgrade spec loader
   odoo-bin -d your_db -u spp_event_spec_loader
   ```

2. **Verify event types appear**:
   - Open event wizard
   - Check that all event types show in dropdown
   - Create test events to verify functionality

### For New Custom Modules

To add event types in your custom module:

```python
# models/my_event.py
from odoo import api, fields, models

class MyCustomEvent(models.Model):
    _name = "spp.event.my.custom"
    _description = "My Custom Event"

    summary = fields.Char()
    custom_field = fields.Text()

    @api.model
    def _register_hook(self):
        """Mark this model as an event model"""
        super()._register_hook()
        ir_model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)
        if ir_model and not ir_model.is_event_model:
            ir_model.sudo().write({"is_event_model": True})
```

Then create a wizard:

```python
# wizard/create_my_event_wizard.py
from odoo import fields, models

class CreateMyEventWizard(models.TransientModel):
    _name = "spp.create.event.my.custom.wizard"
    _description = "Create My Event Wizard"

    event_id = fields.Many2one("spp.event.data")
    summary = fields.Char()
    custom_field = fields.Text()

    def create_event(self):
        event = self.env["spp.event.my.custom"].create({
            "summary": self.summary,
            "custom_field": self.custom_field,
        })
        self.event_id.res_id = event.id
        return event
```

**That's it!** Your event type will automatically appear in the wizard dropdown.

## Testing Checklist

After upgrading:

- [ ] Base wizard shows event types from all modules
- [ ] Can create events using demo types (house visit, phone survey, school enrolment)
- [ ] Can create events using dynamic types (from YAML specs)
- [ ] Generic wizard opens for dynamic types
- [ ] Specific wizards open for demo types
- [ ] Events are properly linked to registrants
- [ ] No errors in server logs
- [ ] All existing events still accessible

## Performance Considerations

### Query Performance

**Before**:

```python
# Multiple queries to different tables
event_type_defs = self.env["spp.event.type.definition"].search(...)
# Plus validation queries per type
```

**After**:

```python
# Single query to core table
event_models = self.env["ir.model"].search([("is_event_model", "=", True)])
```

**Impact**: ✅ Faster - single indexed query vs multiple table scans

### Memory Impact

- Minimal: One boolean field per model
- No additional tables or complex relationships
- Standard Odoo indexing applies

## Future Enhancements

This architecture enables:

1. **Event Type Categories**: Add `event_category` field to group related types
2. **Event Type Metadata**: Add fields for icons, descriptions, help text
3. **Dynamic Wizard Fields**: Generate wizard fields from model field definitions
4. **Event Type Permissions**: Per-type security using the flag
5. **Event Type Statistics**: Easy querying for analytics

## Troubleshooting

### Event types not showing

**Check**:

```python
# In Odoo shell
models = env["ir.model"].search([("is_event_model", "=", True)])
for m in models:
    print(f"{m.model}: {m.name}")
```

**Fix**:

- Ensure module is upgraded: `odoo-bin -d db -u module_name`
- Check `_register_hook` is called (restart Odoo if needed)
- Verify flag is set: Check `ir_model` table in database

### Generic wizard not working

**Check**:

- Wizard model exists: `spp.create.dynamic.event.wizard`
- View exists in `ir.ui.view`
- Security access granted

**Fix**:

- Upgrade `spp_event_spec_loader`
- Check security CSV file loaded
- Verify user has correct groups

## Summary

This refactoring transforms the event type registration from:

- ❌ **Coupled**: Specific table queries
- ❌ **Inflexible**: Hard to extend
- ❌ **Inconsistent**: Different approaches

To:

- ✅ **Decoupled**: Flag-based architecture
- ✅ **Flexible**: Easy to extend
- ✅ **Consistent**: One standard approach

**Result**: A cleaner, more maintainable, and scalable event tracking system! 🚀

---

**Version**: 17.0.1.0.3 **Date**: November 2024 **Status**: ✅ Implemented and Tested **Breaking Changes**:
None (backward compatible)
