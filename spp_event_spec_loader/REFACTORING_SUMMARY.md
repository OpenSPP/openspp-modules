# Refactoring Summary - Cleaner Event Type Architecture

## What Was Done

Refactored the event type registration system to use a **flag-based architecture** instead of module-specific
queries.

## Changes by Module

### 1. ✅ spp_event_data (Base Module)

**Added**:

- `models/ir_model.py` - Boolean field `is_event_model` on `ir.model`
- Dynamic selection in wizard based on the flag
- Generic wizard detection for dynamic models

**Result**: Base module now controls wizard behavior

### 2. ✅ spp_event_demo

**Modified**: All event models (house_visit.py, phone_survey.py, school_enrolment.py)

- Added `_register_hook()` to set `is_event_model = True`

**Result**: Demo event types automatically register themselves

### 3. ✅ spp_event_spec_loader

**Modified**: `models/event_type_definition.py`

- Set `is_event_model = True` when creating dynamic models

**Removed**: `wizard/create_event_wizard.py`

- No longer needed since logic is in base module

**Kept**: `wizard/create_dynamic_event_wizard.py`

- Still needed for handling dynamic models

**Result**: Dynamic models automatically register, cleaner code

## Before vs After

### Before (❌ Coupled)

```
spp_event_spec_loader
└── Overrides wizard in spp_event_data
    └── Queries spp.event.type.definition table
        └── Adds types to selection
```

**Problem**: Derived module controls base behavior

### After (✅ Decoupled)

```
spp_event_data
└── Queries ir.model.is_event_model flag
    ├── spp_event_demo sets flag on its models
    └── spp_event_spec_loader sets flag on dynamic models
```

**Benefit**: Base controls behavior, modules just set flag

## How to Test

```bash
# 1. Upgrade all three modules
odoo-bin -d your_db -u spp_event_data,spp_event_demo,spp_event_spec_loader

# 2. Open event wizard
#    - All event types should appear
#    - Both demo types and dynamic types
#    - Selection updates automatically

# 3. Create events
#    - Test with demo types (house visit, etc.)
#    - Test with dynamic types (from YAML)
#    - Both should work seamlessly
```

## Benefits

| Aspect            | Before           | After        |
| ----------------- | ---------------- | ------------ |
| **Coupling**      | Tight            | Loose        |
| **Extensibility** | Hard             | Easy         |
| **Code Location** | Wrong module     | Right module |
| **Consistency**   | Mixed approaches | One standard |
| **Performance**   | Multiple queries | Single query |

## For Future Developers

To add event types in your custom module:

```python
# 1. Define your model
class MyEvent(models.Model):
    _name = "spp.event.my.event"

    # Your fields...

    @api.model
    def _register_hook(self):
        """Mark as event model"""
        super()._register_hook()
        ir_model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)
        if ir_model:
            ir_model.sudo().write({"is_event_model": True})

# 2. Create your wizard (optional - can use generic one)
class MyEventWizard(models.TransientModel):
    _name = "spp.create.event.my.event.wizard"
    # Your wizard fields and logic...

# 3. That's it! Your type appears in the wizard automatically ✨
```

## Breaking Changes

**None!** This refactoring is fully backward compatible.

- ✅ Existing data preserved
- ✅ Existing functionality maintained
- ✅ No API changes
- ✅ Just cleaner architecture

## Documentation

See **REFACTORING_v17.0.1.0.3.md** for:

- Detailed technical explanation
- Complete code examples
- Migration guide
- Troubleshooting tips
- Architecture diagrams

---

**TL;DR**: Moved wizard logic from `spp_event_spec_loader` to `spp_event_data` base module and used a simple
boolean flag (`is_event_model`) for registration. Much cleaner! ✨

**Status**: ✅ Ready to test **Version**: 17.0.1.0.3
