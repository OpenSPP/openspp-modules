# Code Generator Module - Entity Processing Implementation Guide

## Overview

This document explains the implementation of the YAML entity processing feature in the `spp_code_generator`
module. The feature reads YAML specification files and automatically creates custom fields in `res.partner`
based on the entity definitions.

## Architecture

### Data Flow

```
YAML File Upload → Validation → Parse → Extract Entities → Create Fields → Log Results
```

### Components

1. **Model**: `spp.code.generator` (`models/code_generator.py`)
2. **View**: Form with "Process Entities" button (`views/code_generator_views.xml`)
3. **Target**: `res.partner` model (where fields are created)

---

## Model Fields

### Core Fields

| Field            | Type      | Description                         |
| ---------------- | --------- | ----------------------------------- |
| `name`           | Char      | YAML filename (auto-populated)      |
| `yaml_file`      | Binary    | The uploaded YAML file              |
| `description`    | Text      | User-provided description           |
| `state`          | Selection | Processing status (draft/processed) |
| `processing_log` | Text      | Detailed log of processing results  |

### States

- **draft**: Initial state when YAML is uploaded
- **processed**: After successful entity processing

---

## Key Methods

### 1. `_load_yaml_content()`

**Purpose**: Load and parse the YAML file content

**Process**:

1. Check if YAML file exists
2. Decode binary content (base64)
3. Parse YAML using `yaml.safe_load()`
4. Return Python dictionary

**Returns**: `dict` - Parsed YAML content

**Raises**: `UserError` if file missing or parsing fails

---

### 2. `_get_odoo_field_type(yaml_field_type)`

**Purpose**: Map YAML field types to Odoo field types

**Type Mappings**:

```python
"string"    → "char"
"date"      → "date"
"datetime"  → "datetime"
"enum"      → "selection"
"boolean"   → "boolean"
"integer"   → "integer"
"float"     → "float"
"text"      → "text"
"admin_code"→ "char"
```

**Args**:

- `yaml_field_type` (str): Type from YAML spec

**Returns**: `str` - Odoo field type

---

### 3. `_create_field_from_spec(entity_name, field_spec)`

**Purpose**: Create a single field in `res.partner` from YAML specification

**Process**:

1. Extract field specification (id, label, type, required, etc.)
2. Generate field name with OpenSPP prefix: `z_cst_{field_id}`
3. Check if field already exists (skip if yes)
4. Map YAML type to Odoo type
5. Prepare field values dict
6. Handle special cases (enum/selection fields)
7. Create field using `ir.model.fields`

**Field Naming Convention**:

```
YAML: "hh_id"
Odoo: "z_cst_hh_id"

Prefix breakdown:
- z_     : OpenSPP custom field prefix
- cst_   : Custom (not indicator)
- hh_id  : Original field ID from YAML
```

**Args**:

- `entity_name` (str): Entity name (e.g., "Household")
- `field_spec` (dict): Field specification from YAML

**Field Spec Structure**:

```yaml
{
  "id": "field_name", # Required: Technical name
  "label": "Field Label", # Required: Display label
  "type": "string", # Required: Field type
  "required": True/False, # Optional: Is required?
  "values": [...], # Optional: For enums
  "description": "...", # Optional: Help text
}
```

**Returns**: `ir.model.fields` record or `None` if exists

---

### 4. `action_process_entities()`

**Purpose**: Main processing method - button action

**Process**:

1. Load YAML content
2. Extract "entities" section
3. Initialize processing log
4. For each entity:
   - Get entity details (name, label, fields)
   - For each field:
     - Call `_create_field_from_spec()`
     - Log result (created/skipped/error)
5. Generate summary
6. Update `state` to "processed"
7. Post message in chatter
8. Show success notification

**Returns**: `dict` - Client action (notification)

**Logging**: Creates detailed processing log showing:

- Each entity processed
- Each field created/skipped
- Any errors encountered
- Summary statistics

---

## YAML Structure Example

Based on `4ps_best_practice_example_v7.yaml`:

```yaml
entities:
  - name: "Household"
    label: "4Ps Household"
    fields:
      - id: "hh_id"
        label: "Household ID"
        type: "string"
        required: true
      - id: "province"
        label: "Province"
        type: "admin_code"

  - name: "Individual"
    label: "Member"
    fields:
      - id: "person_id"
        label: "Member ID"
        type: "string"
        required: true
      - id: "birthdate"
        label: "Date of Birth"
        type: "date"
        required: true
      - id: "gender"
        label: "Gender"
        type: "enum"
        values: ["Female", "Male"]
        required: true
```

---

## Field Creation Results

### Example Output

For the above YAML, the following fields would be created in `res.partner`:

| YAML Field ID | Odoo Field Name | Type      | Required |
| ------------- | --------------- | --------- | -------- |
| hh_id         | z_cst_hh_id     | Char      | Yes      |
| province      | z_cst_province  | Char      | No       |
| person_id     | z_cst_person_id | Char      | Yes      |
| birthdate     | z_cst_birthdate | Date      | Yes      |
| gender        | z_cst_gender    | Selection | Yes      |

### Selection Field Example

For `gender` enum field:

```python
Field: z_cst_gender
Type: Selection
Values: [('Female', 'Female'), ('Male', 'Male')]
```

---

## User Interface

### Form View Features

1. **Header**:

   - Status bar (Draft → Processed)
   - "Process Entities" button (visible only in draft state)

2. **Main Section**:

   - YAML filename (large title, readonly)
   - File upload widget
   - Description field

3. **Processing Log Tab**:

   - Shows detailed processing results
   - Only visible after processing

4. **Chatter**:
   - Posts summary message after processing
   - Shows fields created/skipped counts

### Tree View

- Displays filename, state (with colored badge), and description
- State badge colors:
  - Draft: Blue
  - Processed: Green

### Search/Filters

- Filter by state (Draft/Processed)
- Filter by has YAML file
- Group by status

---

## Processing Log Example

```
================================================================================
Processing YAML File: 4ps_best_practice_example_v7.yaml
Started at: 2025-10-23 10:30:00
================================================================================

Entity: Household (4Ps Household)
----------------------------------------
  ✓ Created: hh_id (Household ID) - Type: string
  ✓ Created: province (Province) - Type: admin_code

Entity: Individual (Member)
----------------------------------------
  ✓ Created: person_id (Member ID) - Type: string
  ✓ Created: birthdate (Date of Birth) - Type: date
  ✓ Created: gender (Gender) - Type: enum
  ⊗ Skipped: education_enrollment_status (Education Status) - Already exists

================================================================================
SUMMARY
================================================================================
Total fields created: 5
Total fields skipped: 1
Completed at: 2025-10-23 10:30:15
================================================================================
```

---

## Error Handling

### Validation Errors

- File extension validation (must be .yaml or .yml)
- YAML syntax validation
- Missing required fields in spec

### Processing Errors

- No YAML file uploaded → `UserError`
- Invalid YAML syntax → `UserError` with details
- No "entities" section → `UserError`
- Field creation failure → Logged, processing continues

### Duplicate Fields

- Existing fields are skipped (not recreated)
- Logged as "Skipped" in processing log
- No error raised

---

## OpenSPP Conventions

### Field Naming

Follows OpenSPP field naming patterns:

- `z_`: General prefix for custom fields
- `cst_`: Custom/arbitrary fields (not indicators)
- Example: `z_cst_hh_id`

### Why This Pattern?

1. **z\_**: Groups all custom fields together
2. **cst\_**: Distinguishes from indicators (`ind_`)
3. **Prevents conflicts**: With standard Odoo fields

---

## Best Practices

### 1. YAML File Preparation

- Ensure all required fields (id, label, type) are present
- Use consistent naming conventions
- Provide descriptions for clarity
- Validate YAML syntax before upload

### 2. Field Types

- Use appropriate types (date for dates, enum for choices)
- Provide enum values for selection fields
- Mark fields as required when appropriate

### 3. Processing

- Review the processing log after processing
- Check for skipped fields (may indicate duplicates)
- Check chatter for summary message

### 4. Testing

- Test with small YAML files first
- Verify fields are created correctly in res.partner
- Check field properties (type, required, etc.)

---

## Troubleshooting

### Issue: "No YAML file uploaded"

**Solution**: Upload a YAML file before clicking "Process Entities"

### Issue: "Invalid YAML file"

**Solution**: Validate YAML syntax using online validator or IDE

### Issue: "No 'entities' section found"

**Solution**: Ensure YAML has an `entities` key at the root level

### Issue: Fields not appearing

**Solution**:

1. Check processing log for errors
2. Verify field names don't conflict with existing fields
3. Restart Odoo server to reload model definitions

---

## Future Enhancements

Potential additions for future versions:

1. **Derived Fields Processing**: Handle computed/indicator fields
2. **View Generation**: Auto-create form/tree views for entities
3. **Relationship Handling**: Process one-to-many, many-to-many relationships
4. **Rollback Feature**: Ability to delete created fields
5. **Preview Mode**: Show what would be created before actually creating
6. **Batch Processing**: Process multiple YAML files at once
7. **Field Updates**: Update existing fields instead of skipping

---

## Technical Notes

### Performance

- Fields are created one at a time (not batched)
- Processing is synchronous (no queue jobs)
- Suitable for <100 fields per YAML file

### Database Impact

- Creates records in `ir.model.fields`
- Modifies PostgreSQL schema (adds columns to `res_partner` table)
- Changes are permanent (manual deletion required to remove)

### Security

- Requires System Administrator access to create fields
- Follows Odoo's standard security model
- Field creation logged in processing log and chatter

---

## References

- OpenSPP Field Naming Conventions: See `openspp-fields-naming` cursor rule
- YAML Specification: `4ps_best_practice_example_v7.yaml`
- Odoo Fields Documentation:
  https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#fields

---

**Last Updated**: 2025-10-23 **Module Version**: 17.0.1.3.1 **Author**: OpenSPP.org
