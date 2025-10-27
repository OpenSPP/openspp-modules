# Compute Method Architecture - Indicator Fields

## Overview

This document explains the architecture for generated compute methods in indicator fields, showing how
individual and group indicators are processed differently.

---

## Two-Strategy Approach

### Strategy Matrix

| Indicator Type        | Method Used                         | CEL Profile          | Returns       | Use Case              |
| --------------------- | ----------------------------------- | -------------------- | ------------- | --------------------- |
| **Individual (indv)** | `_exec()`                           | registry_individuals | Boolean       | Individual conditions |
| **Group (grp)**       | `compute_count_and_set_indicator()` | registry_groups      | Boolean/Count | Member aggregation    |

---

## Individual Indicators (indv)

### Architecture

```
┌─────────────────────────────────────────────────┐
│  Individual Indicator                           │
│  (e.g., x_ind_indv_age_yrs)                    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │   _exec()     │  ← Direct CEL execution
         └───────┬───────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  CEL Executor        │
      │  (registry_indiv)    │
      └──────────┬───────────┘
                 │
                 ▼
         ┌───────────────┐
         │  Return True  │  if record matches
         │  or False     │
         └───────────────┘
```

### Generated Code Pattern

```python
for record in self:
    try:
        if record.is_group:
            # Skip groups for individual indicators
            record.x_ind_indv_field_name = None
            continue

        # Execute CEL expression using _exec helper
        result = record._exec(
            'CEL_EXPRESSION_HERE',
            profile='registry_individuals'
        )

        # Check if current record matches
        record.x_ind_indv_field_name = bool(record.id in result.get('ids', []))
    except Exception as e:
        record.x_ind_indv_field_name = None
```

### Example - Age Calculation

**YAML**:

```yaml
- id: "age_yrs"
  label: "Age (years)"
  expression: "age_years(me.birthdate) >= 18"
  dependencies: ["birthdate"]
```

**Generated Compute Method**:

```python
def _compute_age_yrs(self):
    for record in self:
        try:
            if record.is_group:
                record.x_ind_indv_age_yrs = None
                continue

            result = record._exec(
                'age_years(me.birthdate) >= 18',
                profile='registry_individuals'
            )

            record.x_ind_indv_age_yrs = bool(record.id in result.get('ids', []))
        except Exception as e:
            record.x_ind_indv_age_yrs = None
```

**Flow**:

1. Check if record is individual
2. Call `_exec()` with expression
3. CEL executor evaluates expression
4. Returns True if individual is 18+
5. Field updated automatically

---

## Group Indicators (grp)

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Group Indicator                                    │
│  (e.g., x_ind_grp_hh_has_pregnant_member)          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│  compute_count_and_set_indicator()    │  ← Extended in group.py
└────────────────┬───────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │   _exec()     │  ← Called internally
         └───────┬───────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  CEL Executor        │
      │  (registry_groups)   │
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  Domain Conversion   │  ← CEL → Odoo domain
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  Filter Members      │
      └──────────┬───────────┘
                 │
                 ▼
         ┌───────────────┐
         │  Return       │  Boolean (exists) or
         │  Result       │  Integer (count)
         └───────────────┘
```

### Generated Code Pattern

```python
for record in self:
    try:
        if not record.is_group:
            # Skip individuals for group indicators
            record.x_ind_grp_field_name = None
            continue

        # Use compute_count_and_set_indicator with CEL expression
        kinds = None
        domain = []
        cel_expression = 'CEL_EXPRESSION_HERE'

        # Extended method handles CEL → domain conversion
        record.compute_count_and_set_indicator(
            'x_ind_grp_field_name',
            kinds,
            domain,
            presence_only=True,  # Boolean for exists checks
            cel_expression=cel_expression
        )
    except Exception as e:
        record.x_ind_grp_field_name = None
```

### Example - Has Pregnant Member

**YAML**:

```yaml
- id: "hh_has_pregnant_member"
  label: "HH Has Pregnant Member"
  expression: "members.exists(m, m.pregnancy_start_date >= months_ago(9) and m.pregnancy_end_date == null)"
  dependencies: []
```

**Generated Compute Method**:

```python
def _compute_hh_has_pregnant_member(self):
    for record in self:
        try:
            if not record.is_group:
                record.x_ind_grp_hh_has_pregnant_member = None
                continue

            kinds = None
            domain = []
            cel_expression = 'members.exists(m, m.pregnancy_start_date >= months_ago(9) and m.pregnancy_end_date == null)'

            record.compute_count_and_set_indicator(
                'x_ind_grp_hh_has_pregnant_member',
                kinds,
                domain,
                presence_only=True,
                cel_expression=cel_expression
            )
        except Exception as e:
            record.x_ind_grp_hh_has_pregnant_member = None
```

**Flow**:

1. Check if record is group
2. Call `compute_count_and_set_indicator()`
3. Method calls `_exec()` internally with `registry_groups`
4. CEL expression converted to Odoo domain
5. Domain filters group members
6. Returns True if any member matches
7. Field updated automatically

---

## Extended Method in group.py

### Implementation

```python
class GroupRegistry(models.Model):
    _inherit = "res.partner"

    def _exec(self, expr, profile="registry_individuals"):
        """Helper to execute CEL expression."""
        registry = self.env["cel.registry"]
        cfg = registry.load_profile(profile)
        executor = self.env["cel.executor"].with_context(cel_profile=profile, cel_cfg=cfg)
        model = cfg.get("root_model", "res.partner")
        return executor.compile_and_preview(model, expr, limit=50)

    def compute_count_and_set_indicator(self, field_name, kinds, domain, presence_only=False, cel_expression=None):
        if cel_expression:
            # Convert CEL expression to domain
            domain += self._exec(cel_expression, profile="registry_groups").get("domain", [])
            _logger.info(f"CEL expression: {cel_expression} \n => domain: {domain}")

        # Call parent method with augmented domain
        return super().compute_count_and_set_indicator(field_name, kinds, domain, presence_only, cel_expression=None)
```

### Key Points

1. **CEL Expression Handling**:

   - Accepts CEL expression as parameter
   - Calls `_exec()` with `registry_groups` profile
   - Extracts domain from result

2. **Domain Augmentation**:

   - Adds CEL-generated domain to existing domain
   - Passes to parent method

3. **Logging**:
   - Logs CEL expression and resulting domain
   - Useful for debugging

---

## Comparison Table

| Aspect            | Individual (indv)     | Group (grp)                         |
| ----------------- | --------------------- | ----------------------------------- |
| **Entry Point**   | `_exec()` directly    | `compute_count_and_set_indicator()` |
| **CEL Profile**   | registry_individuals  | registry_groups                     |
| **Context**       | Single record (me)    | Members collection                  |
| **Execution**     | Direct evaluation     | Domain conversion + filtering       |
| **Result Format** | Boolean match         | Boolean (exists) or Integer (count) |
| **Use Case**      | Individual properties | Member aggregation                  |
| **Example**       | Age check, date range | Has children, count eligible        |

---

## Benefits of This Architecture

### 1. **Separation of Concerns**

- Individual logic isolated from group logic
- Clear, maintainable code structure
- Easy to debug and test

### 2. **Leverages OpenSPP Infrastructure**

- Uses existing `compute_count_and_set_indicator` method
- Consistent with spp_custom_field patterns
- Integrates with spp_custom_fields_ui

### 3. **CEL Integration**

- Full CEL expression support
- Proper domain conversion
- Helper functions available (age_years, months_ago, etc.)

### 4. **Performance**

- Stored fields for query performance
- Efficient domain-based filtering for groups
- Automatic caching and invalidation

### 5. **Flexibility**

- Easy to extend with new CEL functions
- Can handle complex expressions
- Supports both boolean and count results

---

## Code Generation Process

### 1. Determine Indicator Type

```python
def _determine_indicator_type(self, expression, dependencies):
    group_patterns = [
        "members.exists",
        "members.count",
        "group_membership_ids",
    ]

    if any(pattern in expression.lower() for pattern in group_patterns):
        return "grp"
    return "indv"
```

### 2. Generate Appropriate Code

```python
def _generate_compute_method_code(self, field_name, expression, indicator_type, dependencies):
    if indicator_type == "indv":
        return self._generate_individual_code(field_name, expression)
    elif indicator_type == "grp":
        return self._generate_group_code(field_name, expression)
```

### 3. Create Field with Compute Method

```python
field_values = {
    "name": field_name,
    "ttype": field_type,
    "store": True,
    "compute": f"_compute_{field_id}",
    "target_type": indicator_type,
    "field_category": "ind",
    ...
}
```

---

## Testing Examples

### Test Individual Indicator

```python
# Create individual with birthdate
individual = env['res.partner'].create({
    'name': 'Test Person',
    'is_group': False,
    'birthdate': '2000-01-01'
})

# Trigger computation
individual._compute_age_yrs()

# Check result
print(individual.x_ind_indv_age_yrs)  # True (age >= 18)
```

### Test Group Indicator

```python
# Create group with members
group = env['res.partner'].create({
    'name': 'Test Household',
    'is_group': True
})

# Add member
member = env['res.partner'].create({
    'name': 'Pregnant Member',
    'is_group': False,
    'pregnancy_start_date': fields.Date.today(),
})

# Add to group
env['g2p.group.membership'].create({
    'group': group.id,
    'individual': member.id
})

# Trigger computation
group._compute_hh_has_pregnant_member()

# Check result
print(group.x_ind_grp_hh_has_pregnant_member)  # True
```

---

## Troubleshooting

### Issue: Individual indicator not computing

**Check**:

1. Record is individual (`is_group=False`)
2. `_exec()` method exists in model
3. CEL profile `registry_individuals` exists
4. Expression syntax is valid

### Issue: Group indicator returning None

**Check**:

1. Record is group (`is_group=True`)
2. `compute_count_and_set_indicator()` extended in group.py
3. CEL profile `registry_groups` exists
4. Group has members (group_membership_ids)

---

## References

- **group.py**: Extended compute_count_and_set_indicator
- **cel_executor.py**: CEL expression execution
- **cel_functions.py**: Helper functions (age_years, months_ago, etc.)
- **spp_custom_field**: UI rendering and tab organization
- **spp_custom_fields_ui**: Field management and filtering

---

**Last Updated**: 2025-10-27 **Module**: spp_code_generator v17.0.1.3.1 **Author**: OpenSPP.org
