# OpenSPP Custom Field

The OpenSPP Custom Field module enhances the platform's flexibility by allowing administrators to define and add custom data fields directly to registrant profiles. This capability ensures that OpenSPP can capture highly specific information tailored to the unique needs of various social protection programs and farmer registries.

## Purpose

The OpenSPP Custom Field module enables programs to adapt the platform's data collection capabilities to their precise requirements. It accomplishes this by:

*   **Tailoring Data Collection**: Allows programs to define and add specific data fields to registrant profiles beyond OpenSPP's standard fields.
*   **Enhancing Program Adaptability**: Enables OpenSPP to adapt to the unique data requirements of diverse social protection programs and farmer registries.
*   **Differentiating Data by Registrant Type**: Supports custom fields that are relevant only to individuals or only to groups, ensuring data accuracy. For example, a field for "Primary Crop Type" might only be relevant for a farmer group, while "Marital Status" is for individuals.
*   **Managing Program Indicators**: Provides dedicated sections for displaying read-only indicators, crucial for monitoring and evaluation.
*   **Streamlining Profile Management**: Automatically integrates these custom fields into registrant profiles, creating a comprehensive and program-specific data view.

## Dependencies and Integration

The `spp_custom_field` module integrates seamlessly into the OpenSPP ecosystem, extending core functionalities to provide enhanced data management.

*   **Base (`base`)**: As a fundamental module, `spp_custom_field` relies on the core Odoo framework provided by the `base` module for its underlying data structures and user interface elements.
*   **G2P Registry Base (`g2p_registry_base`)**: This module is a direct extension of the [G2P Registry Base](g2p_registry_base) module. While `g2p_registry_base` establishes the foundational registrant profile, `spp_custom_field` dynamically adds customizable data fields to these profiles, making them more versatile for specific program needs. It leverages the `res.partner` model, which is extended by `g2p_registry_base`, to embed new data points directly within the registrant's record.

## Additional Functionality

The `spp_custom_field` module introduces powerful features for customizing registrant profiles:

### Configurable Registrant Profile Fields

Users can define new data fields, such as text inputs, numerical values, dates, or checkboxes, which then appear on registrant profiles. These fields are intelligently categorized and displayed under a dedicated "Additional Details" tab. This allows programs to capture highly specific information, for instance, "Household Water Source" for social protection programs or "Type of Agricultural Land" for farmer registries. The module also supports creating fields that are specific to either individual registrants or group registrants, ensuring data relevance.

### Dedicated Indicator Section

The module creates a separate "Indicators" tab on registrant profiles. This section is designed to display read-only fields that typically represent program-specific metrics, calculated values, or monitoring data. For example, it could show "Total Benefits Received" or "Number of Dependents Calculated." These fields are for viewing and analysis, providing a quick overview of key performance indicators without allowing direct user input.

### Dynamic Profile Extension

A key capability of this module is its ability to automatically integrate custom and indicator fields into the registrant's profile form. This dynamic integration eliminates the need for manual view modifications whenever new fields are added, significantly simplifying system configuration and maintenance. New fields are immediately accessible and properly categorized within the "Additional Details" or "Indicators" tabs, ensuring a consistent and user-friendly experience.

## Conclusion

The OpenSPP Custom Field module is essential for making OpenSPP a highly adaptable platform, enabling programs to tailor registrant data collection to their precise operational and reporting requirements.