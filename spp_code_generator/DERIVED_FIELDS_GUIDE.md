# Derived Fields (Indicators) Processing Guide

## Overview

This guide explains how the Code Generator module processes `derived_fields` from YAML files to create
computed indicator fields in OpenSPP. Derived fields are computed/calculated fields that automatically update
based on other field values or member data.

## Architecture

### Data Flow

```
YAML derived_fields → Parse → Determine Type → Generate Compute Code → Create Field
```

### Key Components

1. **Model**: `spp.code.generator` (`models/code_generator.py`)
2. **CEL Functions**: Helper functions from `spp_cel_domain` (`cel_functions.py`)
3. **Target**: `res.partner` model with computed indicator fields
4. **Integration**: `spp_custom_fields_ui` for UI display

---

## Field Naming Convention

### Indicator Field Prefixes

Derived fields use **indicator** prefixes (not custom):

- **Group Indicators**: `x_ind_grp_{field_id}`
- **Individual Indicators**: `x_ind_indv_{field_id}`

### Examples

| YAML Field ID          | Entity Type | Odoo Field Name                  | Purpose             |
| ---------------------- | ----------- | -------------------------------- | ------------------- |
| age_yrs                | Individual  | x_ind_indv_age_yrs               | Age in years        |
| ind_pregnant_now       | Individual  | x_ind_indv_ind_pregnant_now      | Currently pregnant  |
| hh_has_pregnant_member | Group       | x_ind_grp_hh_has_pregnant_member | Has pregnant member |

---

## YAML Structure

### Derived Fields Section

```yaml
derived_fields:
  - id: "age_yrs"
    label: "Age (years)"
    expression: "age_years(me.birthdate)"
    purpose: "eligibility, reporting"
    dependencies: ["birthdate"]

  - id: "ind_pregnant_now"
    label: "Currently Pregnant"
    expression: "me.pregnancy_start_date >= months_ago(9) and me.pregnancy_end_date == null"
    purpose: "eligibility, health condition routing"
    dependencies: ["pregnancy_start_date", "pregnancy_end_date"]

  - id: "hh_has_pregnant_member"
    label: "HH Has Pregnant Member"
    expression: "members.exists(m, m.pregnancy_start_date >= months_ago(9) and m.pregnancy_end_date == null)"
    purpose: "eligibility, health grant"
    dependencies: []
```

### Field Specification

Each derived field requires:

- **id** (string, required): Unique field identifier
- **label** (string, required): Human-readable field label
- **expression** (string, required): CEL expression for computation
- **purpose** (string, optional): Business purpose/usage description
- **dependencies** (array, optional): List of field names this indicator depends on

---

## Expression Types

### 1. Individual Expressions (indv)

**Pattern**: CEL expressions evaluated for individual records

```yaml
expression: "age_years(me.birthdate) >= 18"
```

**Generated Code**:

```python
for record in self:
    try:
        if record.is_group:
            record.x_ind_indv_age_yrs = None
            continue

        # Execute CEL expression using _exec helper
        result = record._exec(
            'age_years(me.birthdate) >= 18',
            profile='registry_individuals'
        )

        # Check if current record matches the expression
        record.x_ind_indv_age_yrs = bool(record.id in result.get('ids', []))
    except Exception as e:
        record.x_ind_indv_age_yrs = None
```

**How it works**:

- Uses `_exec()` helper method
- Calls CEL executor with `registry_individuals` profile
- Returns True/False based on whether record matches expression
- Skips group records (only for individuals)

**Use Cases**:

- Age calculations and comparisons
- Date range checks
- Complex individual conditions

---

### 2. Group Aggregation Expressions (grp)

**Pattern**: CEL expressions with member aggregation (exists, count, etc.)

```yaml
expression: "members.exists(m, m.pregnancy_start_date >= months_ago(9) and m.pregnancy_end_date == null)"
```

**Generated Code**:

```python
for record in self:
    try:
        if not record.is_group:
            record.x_ind_grp_hh_has_pregnant_member = None
            continue

        # Use compute_count_and_set_indicator with CEL expression
        # The extended method in group.py will handle domain conversion
        kinds = None
        domain = []
        cel_expression = 'members.exists(m, m.pregnancy_start_date >= months_ago(9) and m.pregnancy_end_date == null)'

        # Call the extended method that processes CEL expressions
        record.compute_count_and_set_indicator(
            'x_ind_grp_hh_has_pregnant_member',
            kinds,
            domain,
            presence_only=True,  # Returns boolean for exists-style checks
            cel_expression=cel_expression
        )
    except Exception as e:
        record.x_ind_grp_hh_has_pregnant_member = None
```

**How it works**:

- Uses `compute_count_and_set_indicator()` method
- Extended in `group.py` to handle CEL expressions
- Converts CEL expression to Odoo domain
- Uses `_exec()` with `registry_groups` profile
- Filters group members based on the criteria
- Returns boolean (presence_only=True) or count

**Use Cases**:

- Household has children under 18
- Group has disabled members
- Family has eligible students
- Count of members matching criteria

---

### 3. Implementation Notes

Both strategies use the same underlying CEL engine but with different entry points:

**Individual Strategy (\_exec)**:

- Directly calls CEL executor
- Uses `registry_individuals` profile
- Evaluates expression in context of individual records
- Returns boolean based on match

**Group Strategy (compute_count_and_set_indicator)**:

- Calls extended method from `group.py`
- Uses `registry_groups` profile
- Converts CEL expression to Odoo domain
- Filters group members
- Supports both boolean (presence_only=True) and count results

**Benefits**:

- Leverages existing OpenSPP infrastructure
- Consistent with spp_custom_fields_ui patterns
- CEL expressions validated and executed properly
- Domain conversion handled automatically

---

## CEL Helper Functions

The following functions are available in expressions (from `cel_functions.py`):

### Date/Time Functions

```python
today()                  # Returns today's date
now()                    # Returns current datetime
days_ago(n)              # Date n days ago
months_ago(n)            # Date n months ago
years_ago(n)             # Date n years ago
age_years(date)          # Calculate age in years from birthdate
```

### Comparison Functions

```python
between(x, a, b)         # Check if x is between a and b (inclusive)
```

### Usage Examples

```yaml
# Age calculation
expression: "age_years(me.birthdate)"

# Pregnancy check (last 9 months)
expression: "me.pregnancy_start_date >= months_ago(9)"

# Age range check
expression: "between(age_years(me.birthdate), 0, 18)"
```

---

## Indicator Type Detection

The system automatically determines if an indicator is for groups or individuals:

### Group Indicators

Detected by presence of:

- `members.exists`
- `members.count`
- `group_membership_ids`
- `compute_count_and_set_indicator`

### Individual Indicators

Default for expressions that:

- Use `me.` for self-reference
- Don't contain group aggregation patterns
- Reference individual fields directly

---

## Field Metadata

### Automatically Set Fields

When creating indicator fields, the system sets:

```python
{
    "ttype": "boolean" or "integer",  # Based on expression analysis
    "store": True,                     # Stored for performance
    "compute": "_compute_{field_id}",  # Compute method name
    "state": "manual",                 # Manual field (can be deleted)
    "target_type": "grp" or "indv",   # For UI filtering
    "field_category": "ind",           # Indicator (not custom)
    "draft_name": field_id,            # Original YAML field ID
    "depends": "field1,field2",        # Dependency fields
    "help": "...",                     # Purpose + expression + dependencies
}
```

### Field Type Determination

```python
if "exists" or "has" or "is_" in expression:
    field_type = "boolean"
elif "count" or "sum" or "age_years" in expression:
    field_type = "integer"
else:
    field_type = "boolean"  # Default
```

---

## Processing Workflow

### Step-by-Step Process

1. **Load YAML File**

   - Parse YAML content
   - Extract `derived_fields` section
   - Validate field specifications

2. **For Each Derived Field**:

   - Extract field metadata (id, label, expression, etc.)
   - Determine indicator type (group/individual)
   - Generate field name with appropriate prefix
   - Check if field already exists (skip if yes)
   - Generate compute method code
   - Determine field type
   - Create field in `ir.model.fields`

3. **Generate Processing Log**:

   - Log each field created/skipped/errored
   - Show expression for each field
   - Generate summary statistics

4. **Update Record**:
   - Append to processing log
   - Post summary in chatter
   - Show success notification

---

## UI Integration

### Form View Buttons

```
┌─────────────────────────────────────────┐
│ [Process Entities] [Process Derived    │  ← Two buttons
│                     Fields]  ● Draft    │
├─────────────────────────────────────────┤
```

### Processing Order

**Recommended**:

1. First: Process Entities (creates base fields)
2. Second: Process Derived Fields (creates indicators)

**Reason**: Derived fields may depend on entity fields

### Field Display

Indicator fields automatically appear in:

- **Indicators Tab** (via `spp_custom_field` module)
- **Group Forms** (for grp indicators)
- **Individual Forms** (for indv indicators)
- **Custom Fields Management** (via `spp_custom_fields_ui`)

---

## Example Processing Log

```
================================================================================
Processing Derived Fields from: 4ps_best_practice_example_v7.yaml
Started at: 2025-10-23 15:30:00
================================================================================

  ✓ Created: age_yrs (Age (years)) - Type: indv indicator
    Expression: age_years(me.birthdate)
  ✓ Created: ind_pregnant_now (Currently Pregnant) - Type: indv indicator
    Expression: me.pregnancy_start_date >= months_ago(9) and me.pregnancy_end_date == null
  ✓ Created: hh_has_pregnant_member (HH Has Pregnant Member) - Type: grp indicator
    Expression: members.exists(m, m.pregnancy_start_date >= months_ago(9) and m.pregnancy_end_date == null)

================================================================================
SUMMARY
================================================================================
Indicator fields created: 3
Indicator fields skipped: 0
Errors encountered: 0
Completed at: 2025-10-23 15:30:15
================================================================================
```

---

## Error Handling

### Common Errors

**1. Invalid Expression Syntax**

```
Error: Failed to parse CEL expression
Solution: Check expression syntax, ensure proper CEL format
```

**2. Missing Dependencies**

```
Error: Field 'birthdate' not found
Solution: Process entities first, or create dependent fields manually
```

**3. Duplicate Field**

```
Skipped: Field x_ind_indv_age_yrs already exists
Solution: Field already created, this is expected behavior
```

### Error Recovery

- Errors are logged but don't stop processing
- Other fields continue to be processed
- Error count shown in summary
- Detailed error messages in processing log

---

## Performance Considerations

### Stored vs Computed

All indicator fields are:

- **Stored**: `store=True` for query performance
- **Computed**: Calculate on demand when dependencies change
- **Indexed**: For fields used in filters

### Dependency Management

The system tracks field dependencies:

```python
depends="birthdate,pregnancy_start_date"
```

This ensures:

- Automatic recomputation when dependencies change
- Efficient update propagation
- Cache invalidation

---

## Advanced Usage

### Custom Compute Logic

For complex scenarios, you can modify the generated compute code by:

1. Creating the field through YAML processing
2. Manually editing the compute method in a custom Python module
3. Inheriting `res.partner` and overriding the compute method

### CEL Expression Testing

Test expressions before adding to YAML:

```python
# In Odoo shell
registry = env['cel.registry']
cfg = registry.load_profile('registry_individuals')
executor = env['cel.executor'].with_context(cel_profile='registry_individuals', cel_cfg=cfg)
result = executor.compile_and_preview(
    'res.partner',
    'age_years(me.birthdate) >= 18',
    limit=10
)
print(result)
```

---

## Best Practices

### 1. Clear Naming

Use descriptive field IDs:

```yaml
✓ Good: age_yrs, ind_pregnant_now, hh_has_children
✗ Bad: field1, calc2, ind3
```

### 2. Document Purpose

Always include purpose:

```yaml
purpose: "eligibility, reporting, payments"
```

### 3. List Dependencies

Explicitly declare dependencies:

```yaml
dependencies: ["birthdate", "pregnancy_start_date"]
```

### 4. Test Expressions

Test expressions with sample data before YAML upload

### 5. Incremental Processing

- Process entities first
- Then process derived fields
- Verify fields appear correctly in UI

---

## Troubleshooting

### Issue: Indicator Not Appearing

**Check**:

1. Field created successfully (check processing log)
2. Target type matches form (grp for groups, indv for individuals)
3. Field category is "ind"
4. Odoo server restarted (for new fields)

### Issue: Computation Error

**Check**:

1. Dependencies exist
2. Expression syntax is valid
3. CEL functions are available
4. Data types match expression expectations

### Issue: Performance Slow

**Solutions**:

1. Ensure fields are stored (`store=True`)
2. Add indexes to frequently filtered fields
3. Optimize complex CEL expressions
4. Consider caching for expensive computations

---

## Integration with Other Modules

### spp_custom_field

- Provides UI rendering for indicator fields
- Creates "Indicators" tab in forms
- Marks fields as readonly (computed)

### spp_custom_fields_ui

- Enables field management
- Provides `target_type` and `field_category` fields
- Filters fields by entity type

### spp_cel_domain

- Provides CEL expression parser
- Handles complex query logic
- Supplies helper functions

---

## Future Enhancements

Potential additions:

1. **Expression Validation**: Pre-validate CEL expressions before field creation
2. **Compute Optimization**: Smart caching for expensive computations
3. **Batch Recomputation**: Efficient bulk recalculation
4. **Expression Builder**: UI for building CEL expressions
5. **Test Data**: Generate test cases from expressions
6. **Performance Metrics**: Track computation time per indicator

---

## References

- OpenSPP Field Naming: See `openspp-fields-naming` cursor rule
- CEL Functions: `spp_cel_domain/services/cel_functions.py`
- Custom Fields UI: `spp_custom_fields_ui/models/custom_fields_ui.py`
- Group Indicators: `spp_code_generator/models/group.py`
- YAML Specification: `4ps_best_practice_example_v7.yaml`

---

**Last Updated**: 2025-10-23 **Module Version**: 17.0.1.3.1 **Author**: OpenSPP.org
