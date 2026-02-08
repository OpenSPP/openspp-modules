# CEL Domain Extensibility Guide

**Date**: 2025-10-01 **Purpose**: Guide for extending CEL with custom functions and profiles from other
modules

---

## Overview

The CEL Domain module supports **optional/soft extensibility** - other modules can contribute CEL functions
and profiles WITHOUT depending on `cel_domain`. If `cel_domain` is installed, extensions auto-activate. If
not, the module works normally.

---

## Extension Methods

### 1. **Function Registry** - Custom CEL Functions

Modules can register custom CEL functions that are available in expressions.

#### Example: Farmer Module

```python
# spp_farmer/__manifest__.py
{
    'name': 'SPP Farmer Registry',
    'depends': [
        'base',
        'g2p_registry_base',
        # NOTE: 'cel_domain' is NOT listed!
    ],
    'post_init_hook': 'post_init_hook',
}
```

```python
# spp_farmer/__init__.py
def post_init_hook(cr, registry):
    """Register CEL extensions if cel_domain is installed."""
    from odoo import api, SUPERUSER_ID
    import logging

    _logger = logging.getLogger(__name__)
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Check if cel_domain is installed
    IrModule = env['ir.module.module']
    cel_module = IrModule.search([
        ('name', '=', 'cel_domain'),
        ('state', '=', 'installed')
    ])

    if cel_module:
        try:
            # Register custom functions
            def crop_season(date_val):
                """Determine crop season from date."""
                if not date_val:
                    return None
                month = date_val.month
                if 3 <= month <= 5:
                    return "planting"
                elif 6 <= month <= 9:
                    return "growing"
                else:
                    return "harvest"

            registry = env['cel.function.registry']
            registry.register('crop_season', crop_season)

            _logger.info("[SPP Farmer] Registered CEL functions")
        except Exception as e:
            _logger.warning(f"[SPP Farmer] Could not register CEL: {e}")
    else:
        _logger.debug("[SPP Farmer] cel_domain not installed, skipping")
```

**Usage in CEL expressions:**

```python
# After registration, users can write:
"crop_season(planting_date) == 'harvest'"
```

---

### 2. **Multi-Module YAML** - Custom Profiles

Modules can contribute CEL profiles without depending on `cel_domain`.

#### Example: Health Module

```yaml
# spp_health/data/cel_profiles.yaml
version: 1
presets:
  # Custom profile for health facilities
  health_facilities:
    root_model: "health.facility"
    base_domain: [["active", "=", true]]
    symbols:
      me:
        model: "health.facility"
      patients:
        relation: "rel"
        through: "health.patient"
        parent: "facility_id"
        link_to: "id"
        child_model: "health.patient"
        default_domain: [["state", "=", "active"]]

  # Extend existing profile
  registry_individuals:
    symbols:
      health_records:
        relation: "rel"
        through: "health.record"
        parent: "partner_id"
        link_field: "id"
        child_model: "health.record"
```

```python
# spp_health/__manifest__.py
{
    'name': 'SPP Health',
    'depends': ['base', 'g2p_registry_base'],  # NO cel_domain!
    'data': [
        'data/cel_profiles.yaml',  # Always included
    ],
}
```

**How it works:**

1. `cel_domain` scans ALL installed modules for `data/cel_profiles.yaml`
2. Profiles are auto-loaded when `cel_domain` is installed
3. If `cel_domain` is NOT installed, YAML file is harmlessly ignored
4. No errors, no failures, just graceful degradation

---

## API Reference

### Function Registry API

```python
registry = env['cel.function.registry']
```

#### `register(name, handler)`

Register a new CEL function.

**Parameters:**

- `name` (str): Function name to use in CEL expressions
- `handler` (callable): Python function that implements the CEL function

**Returns:** `True` if registered, `False` if failed

**Example:**

```python
def is_harvest_time(date_val):
    season = crop_season(date_val)
    return season == "harvest"

registry.register('is_harvest_time', is_harvest_time)
```

#### `unregister(name)`

Remove a registered function.

**Returns:** `True` if unregistered, `False` if not found

#### `get_handler(name)`

Get function handler by name.

**Returns:** Callable or `None`

#### `is_registered(name)`

Check if function is registered.

**Returns:** `bool`

#### `list_functions()`

List all registered function names.

**Returns:** `List[str]`

#### `clear_all()`

Clear all registered functions (useful for testing).

**Returns:** Number of functions cleared

---

## Best Practices

### ✅ DO

1. **Check if cel_domain is installed** before registering functions
2. **Use post_init_hook** for function registration
3. **Log warnings, not errors** if registration fails
4. **Provide meaningful function names** (e.g., `crop_season`, not `func1`)
5. **Document your functions** with docstrings
6. **Test without cel_domain** to ensure graceful degradation

### ❌ DON'T

1. **Don't add cel_domain to `depends`** in manifest
2. **Don't fail module installation** if CEL unavailable
3. **Don't assume function registry exists** without checking
4. **Don't override built-in functions** without good reason
5. **Don't forget error handling** in custom functions

---

## Testing Your Extensions

### Test Function Registration

```python
from odoo.tests import TransactionCase

class TestMyExtension(TransactionCase):
    def setUp(self):
        super().setUp()
        # Register your function
        registry = self.env['cel.function.registry']
        registry.register('my_func', my_function)

    def tearDown(self):
        # Clean up
        self.env['cel.function.registry'].clear_all()
        super().tearDown()

    def test_function_works(self):
        registry = self.env['cel.function.registry']
        self.assertTrue(registry.is_registered('my_func'))

        handler = registry.get_handler('my_func')
        result = handler(test_arg)
        self.assertEqual(result, expected)
```

### Test YAML Profile Loading

```python
def test_custom_profile(self):
    registry = self.env["cel.registry"]

    # Load your custom profile
    profile = registry.load_profile('my_custom_profile')

    # Verify it loaded correctly
    self.assertIn('my_symbol', profile.get('symbols', {}))
```

---

## Real-World Examples

### Example 1: Farmer Module - Crop Seasons

**Use Case:** Filter farmers by current crop season

**Implementation:**

```python
def crop_season(date_val):
    """Return crop season for a given date."""
    if not date_val:
        return None
    month = date_val.month
    if 3 <= month <= 5:
        return "planting"
    elif 6 <= month <= 9:
        return "growing"
    else:
        return "harvest"

env['cel.function.registry'].register('crop_season', crop_season)
```

**CEL Expression:**

```
crop_season(today()) == "planting"
```

---

### Example 2: Health Module - Vaccination Status

**Use Case:** Find children due for vaccination

**Implementation:**

```python
def is_vaccination_due(birthdate):
    """Check if person is due for vaccination (2-6 months old)."""
    if not birthdate:
        return False
    age_months = (date.today() - birthdate).days / 30
    return 2 <= age_months <= 6

env['cel.function.registry'].register('is_vaccination_due', is_vaccination_due)
```

**CEL Expression:**

```
is_vaccination_due(birthdate)
```

---

### Example 3: Education Module - School Age

**Use Case:** Find school-aged children

**YAML Profile:**

```yaml
# spp_education/data/cel_profiles.yaml
version: 1
presets:
  school_enrollment:
    root_model: "education.student"
    base_domain: [["active", "=", true]]
    symbols:
      me:
        model: "education.student"
      school:
        relation: "many2one"
        field: "school_id"
        model: "education.school"
```

**CEL Expression:**

```
between(age_years(birthdate), 6, 18) and not enrolled
```

---

## Architecture

### Extensibility Flow

```
1. Module Install (e.g., spp_farmer)
   ↓
2. post_init_hook executes
   ↓
3. Check if cel_domain installed
   ↓
4a. If YES: Register functions/profiles
4b. If NO: Skip silently
   ↓
5. Module works normally
```

### Function Registry Check Flow

```
CEL Expression: "crop_season(date)"
   ↓
1. Translator checks function registry
   ↓
2a. Found: Execute registered handler
2b. Not found: Check built-in functions
   ↓
3. Generate domain
```

### YAML Profile Discovery

```
cel_domain loads
   ↓
Scan all installed modules
   ↓
For each module:
  - Check for data/cel_profiles.yaml
  - If found: Load and merge profiles
   ↓
Profiles available for use
```

---

## Troubleshooting

### Function not executing

**Symptom:** Custom function not working in CEL expressions

**Checklist:**

1. ✓ Is `cel_domain` installed?
2. ✓ Did `post_init_hook` run successfully?
3. ✓ Check logs for registration messages
4. ✓ Verify function is registered: `env['cel.function.registry'].list_functions()`

### Profile not found

**Symptom:** Custom profile not available

**Checklist:**

1. ✓ Is YAML file named `cel_profiles.yaml`?
2. ✓ Is it in `module_name/data/` directory?
3. ✓ Is it listed in manifest `data` section?
4. ✓ Check logs for YAML loading messages

### Module fails to install

**Problem:** Module crashes when `cel_domain` not installed

**Solution:** Wrap CEL code in try/except:

```python
try:
    if 'cel.function.registry' in env:
        registry = env['cel.function.registry']
        registry.register('my_func', my_func)
except Exception as e:
    _logger.debug(f"CEL not available: {e}")
```

---

## Test Results

**Extensibility Test Suite:** 13 tests, all passing ✅

1. `test_function_registry_basic` - Basic registration/retrieval
2. `test_function_registry_unregister` - Unregister functions
3. `test_function_registry_invalid_handler` - Invalid handler rejection
4. `test_function_registry_override_warning` - Override warnings
5. `test_function_registry_clear_all` - Clear all functions
6. `test_custom_function_in_expression` - Use in expressions
7. `test_custom_function_with_arguments` - Functions with args
8. `test_extensibility_example_crop_season` - Crop season example
9. `test_extensibility_example_health_check` - Health check example
10. `test_function_registry_isolation` - No interference with built-ins
11. `test_multi_module_yaml_loading` - Multi-module YAML discovery
12. `test_profile_loading_precedence` - Profile precedence
13. `test_yaml_loading_graceful_degradation` - Graceful failures

---

## See Also

- `cel_domain/models/cel_function_registry.py` - Function registry implementation
- `cel_domain/models/cel_registry.py` - Multi-module YAML loading
- `cel_domain/tests/test_cel_extensibility.py` - Extensibility tests
- `cel_domain/USER_GUIDE.md` - CEL expression syntax guide
- `cel_domain/EXTERNAL_METRICS_SPEC_V2.md` - Final spec for external metrics (providers, caching, push/pull)

---

**Last Updated**: October 1, 2025
