# spp_demo_common Tests

This directory contains comprehensive test coverage for all Python functions in the `spp_demo_common` module
for CodeCov.

## Test Files

### test_demo_data_generator.py (27 tests)

Tests for the demo data generator functionality including:

- Default value methods
- Job queue computation
- Group and individual generation
- ID generation from regex patterns
- Bank account creation
- Phone number generation
- GPS coordinates generation
- Head member identification
- Complete demo data generation workflows

### test_data_export.py (22 tests)

Tests for data export functionality including:

- Export configuration
- Model and module selection
- Raw data extraction
- JSON export file generation
- Template management
- State transitions
- Binary data handling

### test_data_import.py (32 tests)

Tests for data import functionality including:

- Import file parsing
- Data validation
- Record creation
- Many2one and many2many field processing
- Dependency resolution
- State transitions
- Error handling
- Existing record detection

### test_res_config_settings.py (10 tests)

Tests for configuration settings including:

- All config parameter fields
- Setting and getting config values
- Multiple parameter updates
- Default value handling

### test_res_country.py (12 tests)

Tests for country model extensions including:

- GPS bounds (lat/lon min/max)
- Faker locale configuration
- Field precision
- Search functionality

### test_res_partner.py (15 tests)

Tests for partner model extensions including:

- Demo generator relationships
- GPS coordinates field
- Group vs individual differentiation
- One2many relations

### test_apps_wizard.py (17 tests)

Tests for apps wizard functionality including:

- Not installed modules handling
- Missing modules tracking
- Module installation workflow
- Wizard relations

## Running Tests

To run all tests:

```bash
odoo-bin -d <database> -i spp_demo_common --test-enable --stop-after-init
```

To run specific test class:

```bash
odoo-bin -d <database> -i spp_demo_common --test-enable --test-tags=spp_demo_common --stop-after-init
```

To run specific test file:

```bash
odoo-bin -d <database> --test-enable --test-tags=/spp_demo_common:TestDemoDataGenerator --stop-after-init
```

## Test Coverage

Total test methods: **135+ tests**

All Python functions and methods in the following models are covered:

- `spp.demo.data.generator` (main model + ID/Bank types)
- `spp.data.exporter` (main model + templates + raw)
- `spp.data.importer` (main model + raw + summary)
- `res.config.settings` (inherited)
- `res.country` (inherited)
- `res.partner` (inherited)
- `spp.apps.wizard` (main model + missing modules)

## Test Patterns

All tests follow OpenSPP testing best practices:

- Extend `TransactionCase` for database transactions
- Set up test data in `setUpClass` method
- Use descriptive test names with `test_XX_` prefix
- Include docstrings explaining test purpose
- Test both success and edge cases
- Verify field existence and types
- Test model relationships and computed fields

## CodeCov Integration

These tests are designed to maximize code coverage for CodeCov reports. They cover:

- All public methods
- Default value methods
- Computed fields
- Action methods
- Validation logic
- Error handling
- Edge cases and boundary conditions
