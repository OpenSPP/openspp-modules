# OpenSPP Registry Name Suffix

The `spp_registry_name_suffix` module adds a configurable suffix field to Individual registrant names in OpenSPP, enabling proper recording of name suffixes such as Jr., Sr., III, IV, PhD, MD, etc.

## Purpose

This module enhances individual registrant data by:

* **Providing configurable suffixes**: Administrators can manage available suffixes through the Registry Configuration menu.
* **Adding suffix support**: Record name suffixes using a standardized Many2one field reference.
* **Extending name generation**: Automatically includes the suffix in the computed full name.
* **Maintaining data integrity**: The suffix is stored as a reference to a configurable suffix record.

## Features

### Suffix Configuration
A new "Name Suffixes" menu is available under Registry > Configuration, allowing administrators to:
- Create, edit, and archive name suffixes
- Define suffix codes for data integration
- Set display order using sequence numbers
- Add descriptions for suffix usage guidance

### Pre-configured Suffixes
The module comes with commonly used suffixes:
- **Generational**: Jr., Sr., I, II, III, IV, V
- **Academic/Professional**: PhD, MD, Esq.

### Individual Registrant Integration
The suffix field appears on the Individual registrant form after the "Additional Name" field. It uses a dropdown selection with the following features:
- Quick search by suffix name or code
- No inline creation (to maintain data quality)
- Optional display in the registrant list view

### Automatic Name Generation
The suffix is automatically appended to the registrant's computed name in the format:
`FAMILY_NAME, GIVEN_NAME, ADDL_NAME, SUFFIX`

For example: "SMITH, JOHN, MICHAEL, JR."

## Dependencies

This module depends on:
- **spp_registrant_import**: Provides the base name computation logic for registrants.
- **g2p_registry_individual**: Provides the individual registrant views and model.

## Configuration

1. Navigate to Registry > Configuration > Name Suffixes
2. Create additional suffixes as needed for your implementation
3. Set the sequence to control display order in dropdowns

## Usage

1. Navigate to an Individual registrant form
2. Select a suffix from the "Suffix" dropdown field
3. The full name will automatically update to include the suffix

## References

- OpenG2P Registry Individual: https://github.com/OpenSPP/openg2p-registry/tree/17.0-develop-openspp/g2p_registry_individual

