# OpenSPP Event Spec Loader - Usage Guide

## Overview

The `spp_event_spec_loader` module dynamically generates event data types from YAML program specifications. This guide explains how to use it effectively.

## Quick Start

### 1. Install the Module

```bash
# Ensure pyyaml is installed
pip install pyyaml

# Install module via Odoo
# Apps → Search "Event Spec Loader" → Install
```

### 2. Create Your First Program Specification

1. Navigate to: **Registry → Configuration → Event Spec Loader → Program Specifications**
2. Click **Create**
3. Fill in:
   - **Name**: Your program name (e.g., "4Ps Program")
   - **Code**: Unique code (e.g., "4PS")
4. **Upload YAML File**:
   - Go to "Upload YAML" tab
   - Click "Upload your file" button
   - Select your `.yaml` file
   - The content will automatically populate
   
   OR
   
   **Enter Manually**:
   - Go to "YAML Specification" tab
   - Paste or type your YAML content

### 3. Validate the Specification

1. Click **Validate** button
2. Review extracted metadata in tabs:
   - **Program Metadata**: Objectives, agencies, etc.
   - **Parsed Data**: JSON representation
   - **Errors**: Any validation errors

### 4. Deploy Event Types

1. Click **Deploy Event Types** button
2. System will:
   - Extract event types from YAML
   - Create models for each event type
   - Generate views (tree/form)
   - Register with event framework

3. Click the **Event Types** smart button to view created types

### 5. Use Generated Event Types

Generated event types are automatically available:
- In registrant forms (via "Event Data" button)
- In the event creation wizard
- In event data management views

## YAML Structure Reference

### Template Files

The module includes two ready-to-use templates:

### 1. Simple Template (`program_spec_simple_template.yaml`)

Perfect for quick start - minimal configuration:

```yaml
program:
  name: "My Program Name"
  currency: "USD"
  localization:
    languages: ["en"]

event_types:
  - id: "my_first_event"
    name: "My First Event"
    model: "spp.event.my.first.event"
    fields:
      - name: "event_date"
        label: "Date"
        field_type: "date"
      - name: "notes"
        label: "Notes"
        field_type: "text"
```

### 2. Complete Template (`program_spec_template.yaml`)

Comprehensive template with all available options - use as reference.

### Complete Example with External Systems

```yaml
program:
  name: "Conditional Cash Transfer Program"
  objectives:
    - "Improve education outcomes"
    - "Enhance health indicators"
  currency: "PHP"
  localization:
    languages: ["en", "fil"]
  implementing_agencies: ["DSWD", "DepEd"]

# External systems generate event types automatically
external_systems:
  - id: "EducationSystem"
    role: "evidence_provider"
    domain: "education"
    data_contract:
      record_type: "attendance"
      required_fields:
        - name: "attendance_pct"
          type: "number"
        - name: "school_id"
          type: "string"
        - name: "period"
          type: "string"

# Compliance conditions generate verification event types
compliance:
  conditions:
    - id: "attendance_check"
      description: "Verify school attendance ≥85%"
    - id: "health_checkup"
      description: "Health facility visit completed"

# Custom event types for program-specific needs
event_types:
  - id: "house_visit"
    name: "House Visit"
    model: "spp.event.house.visit.custom"
    description: "Field assessment"
    fields:
      - name: "location_gps"
        label: "GPS Coordinates"
        field_type: "char"
      - name: "household_size"
        label: "Household Size"
        field_type: "float"
      - name: "visit_notes"
        label: "Notes"
        field_type: "text"
```

## Generated Event Types

From the above example, the system generates:

1. **spp.event.education.attendance** (from external_systems)
   - Fields: attendance_pct, school_id, period

2. **spp.event.compliance.attendance_check** (from compliance.conditions)
   - Fields: verified_by, verification_date, result, notes

3. **spp.event.compliance.health_checkup** (from compliance.conditions)
   - Fields: verified_by, verification_date, result, notes

4. **spp.event.house.visit.custom** (from event_types)
   - Fields: location_gps, household_size, visit_notes

## Field Type Mapping

| YAML Type | Odoo Field Type | Example |
|-----------|----------------|---------|
| `string` | `char` | Text input |
| `number` | `float` | Decimal number |
| `boolean` | `boolean` | Checkbox |
| `date` | `date` | Date picker |
| `datetime` | `datetime` | Date + time picker |
| `text` | `text` | Multiline text |

## Using the 4Ps Example YAML

To use the 4Ps example specification:

1. Download the example: `4ps_best_practice_example_v7.yaml`
2. Create a new Program Specification
3. Go to "Upload YAML" tab
4. Upload the downloaded file
5. Validate and deploy

This will create event types for:
- Education attendance tracking
- Health checkups
- Compliance verification
- House visits
- Grievance management

## Advanced Usage

### Updating an Existing Specification

1. Open the Program Specification
2. Click **Reset to Draft**
3. Modify YAML content
4. Click **Validate** → **Deploy Event Types**
5. Existing event types are updated, new ones are created

### Undeploying Event Types

To remove views but preserve data:

1. Go to **Event Type Definitions**
2. Select an event type
3. Click **Undeploy**
4. Views are removed, model data is preserved

### Managing Multiple Programs

Each program specification is independent:
- Create separate specs for different programs
- Event types are namespaced by program
- Deploy/undeploy independently

## Troubleshooting

### "Invalid YAML syntax" Error

**Problem**: YAML is not properly formatted

**Solution**:
- Check indentation (use spaces, not tabs)
- Validate YAML at https://yamllint.com
- Check for missing colons or quotes

### Event Type Not Appearing in Wizard

**Problem**: Dynamic selection field not updated

**Solution**:
- Restart Odoo service
- Or manually add to `spp.create.event.wizard.event_data_model` selection

### "Model already exists" Warning

**Problem**: Attempting to redeploy existing model

**Solution**:
- This is normal, the system updates the existing model
- To start fresh, delete via: Settings → Technical → Database Structure → Models

### Fields Not Showing in Views

**Problem**: Generated views are cached

**Solution**:
- Clear browser cache
- Restart Odoo
- Or manually refresh views via Technical menu

## Best Practices

### 1. Version Control Your YAML

Keep specifications in git:

```bash
# Create a specs directory
mkdir openspp-specs
cd openspp-specs
git init

# Save each program spec
vim 4ps_program.yaml
git add 4ps_program.yaml
git commit -m "Initial 4Ps specification"
```

### 2. Test with Sample Data

Before deploying to production:
- Create test registrants
- Create test events using new types
- Verify field validations
- Test reporting queries

### 3. Document Field Purposes

Use YAML comments:

```yaml
fields:
  - name: "attendance_pct"
    label: "Attendance Percentage"
    field_type: "number"
    # Range: 0-100
    # Source: School monthly reports
    # Used for: Compliance checking
```

### 4. Namespace Your Models

Use clear, namespaced technical names:

```yaml
# Good
model: "spp.event.4ps.house.visit"

# Avoid
model: "spp.event.visit"
```

### 5. Incremental Deployment

Start small:
- Deploy with 1-2 event types
- Test thoroughly
- Add more event types gradually

## Integration with Existing Modules

### With spp_event_demo

Generated event types work alongside spp_event_demo:
- Both appear in event creation wizard
- Both use spp.event.data framework
- Mix and match as needed

### With Custom Modules

Extend generated event types:

```python
class CustomEventExtension(models.Model):
    _inherit = "spp.event.education.attendance"
    
    # Add custom fields or methods
    custom_field = fields.Char("Custom Data")
```

## Performance Considerations

- **Model Count**: Limit to 20-30 event types per deployment
- **Field Count**: Keep to 10-15 fields per event type
- **Deployment Time**: Can take 30-60 seconds for large specs
- **Database Size**: Each model adds ~10KB overhead

## Support and Contribution

- **Bug Reports**: https://github.com/OpenSPP/openspp-modules/issues
- **Documentation**: https://docs.openspp.org
- **Community**: https://github.com/OpenSPP/openspp-modules/discussions

## Example Workflows

### Workflow 1: Adding a New Program

```
1. Receive program requirements document
2. Convert to YAML specification
3. Create Program Spec in Odoo
4. Validate specification
5. Deploy event types
6. Train staff on new event types
7. Begin data collection
```

### Workflow 2: Modifying Existing Program

```
1. Click "Export YAML" to download current specification
2. Modify in your text editor
3. Reset spec to draft
4. Upload updated YAML file (or paste manually)
5. Validate and review changes
6. Deploy updates
7. Test with sample data
```

### Workflow 3: Program Retirement

```
1. Stop creating new events
2. Export historical event data
3. Undeploy event types
4. Archive program specification
5. Preserve data for reporting
```

## Appendix: Full YAML Schema

See the `4ps_best_practice_example_v7.yaml` for a complete, production-ready example with:
- Complex eligibility rules
- Multiple entitlement components
- External system integrations
- Compliance conditions
- Calendar definitions
- Reference tables
- Security policies

This file serves as the canonical template for program specifications.

