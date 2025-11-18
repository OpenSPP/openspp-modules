# Testing Checklist - Event Type Refactoring

## Pre-Upgrade Checklist

Before upgrading, verify:

- [ ] Database backup completed
- [ ] Current event types are working
- [ ] Can create events with existing types
- [ ] Note down which event types are currently visible

## Upgrade Process

Execute in this order:

```bash
# Step 1: Upgrade base module
odoo-bin -d your_database -u spp_event_data

# Step 2: Upgrade demo module
odoo-bin -d your_database -u spp_event_demo

# Step 3: Upgrade spec loader module
odoo-bin -d your_database -u spp_event_spec_loader

# OR upgrade all at once
odoo-bin -d your_database -u spp_event_data,spp_event_demo,spp_event_spec_loader
```

## Post-Upgrade Verification

### 1. Check Database Flag

```sql
-- Check that event models have the flag set
SELECT model, name, is_event_model
FROM ir_model
WHERE model LIKE 'spp.event.%'
ORDER BY model;
```

**Expected Results**:

- `spp.event.house.visit` - `is_event_model = True`
- `spp.event.phone.survey` - `is_event_model = True`
- `spp.event.schoolenrolment.record` - `is_event_model = True`
- Any dynamic models from YAML - `is_event_model = True`

### 2. Check Wizard Selection

In Odoo shell:

```python
# Check what the wizard shows
wizard = env['spp.create.event.wizard'].create({})
selection = wizard._get_event_data_model_selection()
print("Event types in wizard:")
for model, name in selection:
    print(f"  {model}: {name}")
```

**Expected**: All event types should be listed

### 3. UI Testing

#### Test Demo Event Types

- [ ] Open: Registry → Groups (or Individuals)
- [ ] Select a registrant
- [ ] Click "Event Data" button/action
- [ ] Wizard opens
- [ ] Event Type dropdown shows:
  - [ ] "None" (default)
  - [ ] "House Visit"
  - [ ] "Phone Survey"
  - [ ] "School Enrolment Record"

#### Test Creating Demo Events

For each demo type:

**House Visit**:

- [ ] Select "House Visit" from dropdown
- [ ] Select registrant
- [ ] Set collection date
- [ ] Click "Next"
- [ ] Specific wizard opens (spp.create.event.house.visit.wizard)
- [ ] Fill in fields (is_farm, farm_size, etc.)
- [ ] Click "Create Event"
- [ ] Event created successfully
- [ ] Event visible in registrant's event list

**Phone Survey**:

- [ ] Select "Phone Survey"
- [ ] Specific wizard opens
- [ ] Can create event
- [ ] Event saves correctly

**School Enrolment**:

- [ ] Select "School Enrolment Record"
- [ ] Specific wizard opens
- [ ] Can create event
- [ ] Event saves correctly

#### Test Dynamic Event Types (from YAML)

- [ ] Deploy a YAML specification with event types
- [ ] Verify dynamic types appear in dropdown
- [ ] Select a dynamic event type
- [ ] Generic wizard opens (spp.create.dynamic.event.wizard)
- [ ] Fill in name, summary, description
- [ ] Click "Create Event"
- [ ] Event created successfully
- [ ] Event linked to registrant

### 4. Backward Compatibility

- [ ] Existing event records still accessible
- [ ] Can view existing event data
- [ ] Can edit existing events (if allowed)
- [ ] No data loss or corruption
- [ ] All relationships preserved

### 5. Error Handling

Test edge cases:

- [ ] Select "None" → Appropriate handling
- [ ] Cancel wizard → No orphan records
- [ ] Missing required fields → Validation errors shown
- [ ] Duplicate event creation → Handled correctly

### 6. Log Verification

Check server logs for:

```bash
# Should see logs like:
# INFO: Added event type to wizard: spp.event.house.visit (House Visit)
# INFO: Added event type to wizard: spp.event.phone.survey (Phone Survey)
# DEBUG: Using generic wizard for model x_spp_event_...
```

- [ ] No ERROR level logs
- [ ] No WARNING about missing models
- [ ] INFO logs show event types being registered

### 7. Performance Check

- [ ] Wizard opens quickly (< 1 second)
- [ ] No noticeable lag when selecting event type
- [ ] Event creation is fast
- [ ] No database query timeout warnings

## Troubleshooting Tests

### If event types don't appear:

```python
# Check flag is set
models = env["ir.model"].search([("model", "like", "spp.event.%")])
for m in models:
    print(f"{m.model}: is_event_model={m.is_event_model}")

# If False, manually set it
model = env["ir.model"].search([("model", "=", "spp.event.house.visit")])
model.sudo().write({"is_event_model": True})
```

### If wizard doesn't open:

```python
# Check wizard exists
wizard_model = "spp.create.event.house.visit.wizard"
exists = wizard_model in env
print(f"Wizard {wizard_model} exists: {exists}")

# Check view exists
view = env["ir.ui.view"].search([
    ("model", "=", wizard_model),
    ("type", "=", "form")
])
print(f"View ID: {view.id if view else 'Not found'}")
```

### If generic wizard fails:

```python
# Check generic wizard
generic = "spp.create.dynamic.event.wizard"
exists = generic in env
print(f"Generic wizard exists: {exists}")

view = env["ir.ui.view"].search([
    ("model", "=", generic),
    ("type", "=", "form")
])
print(f"Generic view ID: {view.id if view else 'Not found'}")
```

## Regression Testing

Ensure no regression in:

- [ ] Event data viewing
- [ ] Event filtering
- [ ] Event searching
- [ ] Event reporting
- [ ] Event data export
- [ ] Event statistics/counts
- [ ] Related registrant links

## Clean Installation Test

For comprehensive testing, try clean install:

```bash
# Create new database
createdb test_event_refactor

# Install modules
odoo-bin -d test_event_refactor -i spp_event_data,spp_event_demo,spp_event_spec_loader

# Verify everything works from scratch
```

## Sign-off Checklist

Before considering complete:

- [ ] All event types visible in wizard
- [ ] Can create events with demo types
- [ ] Can create events with dynamic types
- [ ] Existing events accessible
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] Team notified of changes

## Known Limitations

Document any known issues:

- Module restart may be needed after deploying new YAML specs
- Generic wizard only shows basic fields (name, summary, description)
- Custom wizard fields not dynamically generated (yet)

## Success Criteria

✅ **PASS** if:

- All event types appear in wizard
- Can create and view events
- No data loss
- No errors in logs
- Backward compatible

❌ **FAIL** if:

- Event types missing from wizard
- Cannot create events
- Errors in logs
- Data loss or corruption
- Breaking changes for existing features

---

**Test Date**: **\*\***\_\_\_**\*\*** **Tested By**: **\*\***\_\_\_**\*\*** **Database**:
**\*\***\_\_\_**\*\*** **Status**: [ ] PASS [ ] FAIL **Notes**:
