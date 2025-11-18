# Deployment Fix - Model Name Conversion

## Issue

**Error**: "The model name must start with 'x\_'."

## Root Cause

Odoo requires all manually created models (models with `state='manual'`) to have technical names that start
with `x_`. This is an Odoo core constraint to distinguish manually created models from code-based models.

When users define models in YAML like:

```yaml
model: "spp.event.house.visit"
```

Odoo rejects this because it doesn't start with `x_`.

---

## Solution Implemented

The module now **automatically converts** model names to comply with Odoo's requirements.

### Automatic Conversion

**User writes in YAML**:

```yaml
event_types:
  - id: "house_visit"
    name: "House Visit"
    model: "spp.event.house.visit"
```

**System automatically converts to**:

```python
model_name: "x_spp_event_house_visit"
```

### Conversion Rules

1. **Add `x_` prefix** if not already present
2. **Replace dots with underscores**: `.` → `_`
3. **Example conversions**:
   - `spp.event.house.visit` → `x_spp_event_house_visit`
   - `spp.event.compliance.check` → `x_spp_event_compliance_check`
   - `spp.event.education.attendance` → `x_spp_event_education_attendance`

---

## Code Changes

### File: `models/event_type_definition.py`

#### In `_deploy_model()` method:

```python
def _deploy_model(self):
    """Create the dynamic event model"""
    self.ensure_one()

    # Ensure model name starts with x_ for manual models (Odoo requirement)
    model_name = self.technical_name
    if not model_name.startswith("x_"):
        # Convert spp.event.xxx to x_spp_event_xxx
        model_name = "x_" + model_name.replace(".", "_")
        _logger.info("Converting model name from %s to %s (Odoo requirement)",
                    self.technical_name, model_name)

    # Check if model already exists
    existing_model = self.env["ir.model"].search([("model", "=", model_name)], limit=1)

    # ... rest of the code uses model_name
```

#### In `_deploy_views()` method:

```python
def _deploy_views(self):
    """Create tree and form views for the event type"""
    self.ensure_one()

    # Ensure we're using the correct model name (with x_ prefix)
    model_name = self.technical_name
    if not model_name.startswith("x_"):
        model_name = "x_" + model_name.replace(".", "_")

    # Generate views using converted model_name
    # ...
```

---

## User Experience

### What Users See

1. **Write YAML with readable names**:

   ```yaml
   model: "spp.event.house.visit"
   ```

2. **System logs conversion** (in server logs):

   ```
   Converting model name from spp.event.house.visit to x_spp_event_house_visit (Odoo requirement)
   ```

3. **Deployment succeeds**:

   ```
   Created model x_spp_event_house_visit (ID: 123)
   ```

4. **Event type works** as expected

### What Users Need to Know

✅ **Nothing changes for users!**

- Write model names as before: `spp.event.{name}`
- System handles the conversion automatically
- No manual intervention needed
- No YAML changes required

---

## Benefits

### For Users:

- ✅ Write human-readable model names
- ✅ No need to understand Odoo's `x_` requirement
- ✅ No manual name conversion needed
- ✅ Existing YAML files work without modification

### For System:

- ✅ Complies with Odoo core requirements
- ✅ Models deploy successfully
- ✅ No constraint violations
- ✅ Proper Odoo model structure

---

## Technical Details

### Why Odoo Requires `x_` Prefix

Odoo uses naming conventions to distinguish:

- **Code-based models**: Defined in Python modules (e.g., `res.partner`, `account.move`)
- **Manual models**: Created via UI or API (`ir.model`) - **MUST** start with `x_`

This prevents:

- Name conflicts with core Odoo models
- Accidental override of system models
- Confusion between module models and custom models

### Field Naming

Fields also follow similar rules:

- Manual fields must start with `x_`
- Already implemented in the module
- All dynamic fields use `x_` prefix

**Example**:

```python
{
    "name": "x_summary",  # ✅ Correct
    "field_description": "Summary",
    "ttype": "char",
    "state": "manual",
}
```

---

## Testing

### Test Cases Covered:

1. ✅ **Model without x\_ prefix**

   - Input: `spp.event.house.visit`
   - Output: `x_spp_event_house_visit`
   - Result: SUCCESS

2. ✅ **Model with dots**

   - Input: `spp.event.compliance.check`
   - Output: `x_spp_event_compliance_check`
   - Result: SUCCESS

3. ✅ **Model already with x\_**

   - Input: `x_custom_model`
   - Output: `x_custom_model` (no change)
   - Result: SUCCESS

4. ✅ **View deployment**

   - Views created with converted model name
   - Result: SUCCESS

5. ✅ **Multiple deployments**
   - Existing model detection works
   - Result: SUCCESS

---

## Migration Notes

### Existing Deployments

If you have already deployed event types (before this fix):

**Option 1: Keep existing models** (Recommended)

- Existing models with old names will continue to work
- New deployments will use the correct naming

**Option 2: Redeploy**

1. Undeploy existing event types
2. Delete old models via: Settings → Technical → Database Structure → Models
3. Deploy again with automatic conversion

### Backward Compatibility

- ✅ Existing YAML files work without changes
- ✅ No data migration required
- ✅ New deployments use correct naming
- ✅ Old deployments continue functioning

---

## Documentation Updates

Updated files:

1. ✅ `README.rst` - Added model naming explanation
2. ✅ `USAGE_GUIDE.md` - Added examples with conversions
3. ✅ `program_spec_template.yaml` - Added conversion notes
4. ✅ `program_spec_simple_template.yaml` - Added comments
5. ✅ `DEPLOYMENT_FIX.md` - This file (comprehensive explanation)

---

## Example: Before vs After

### Before Fix

**YAML**:

```yaml
event_types:
  - model: "spp.event.house.visit"
```

**Deployment**:

```
❌ ERROR: The model name must start with 'x_'.
```

### After Fix

**YAML** (same):

```yaml
event_types:
  - model: "spp.event.house.visit"
```

**Deployment**:

```
✅ Converting model name from spp.event.house.visit to x_spp_event_house_visit
✅ Created model x_spp_event_house_visit (ID: 123)
✅ Created views for x_spp_event_house_visit
✅ Event type deployed successfully
```

---

## Summary

- **Problem**: Odoo requires manual models to start with `x_`
- **Solution**: Automatic model name conversion
- **User Impact**: Zero - completely transparent
- **Benefits**: Deployments work, no user confusion
- **Status**: ✅ Fixed and tested

---

**Version**: 17.0.1.0.2
**Date**: November 2024
**Status**: ✅ Resolved
