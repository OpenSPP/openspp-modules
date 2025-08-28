# OpenSPP Custom Fields Ui

The OpenSPP Custom Fields UI module provides a user-friendly interface for program implementers to define and manage custom data fields for registrants within the OpenSPP platform. This allows for tailoring data collection to the unique requirements of various social protection programs and farmer registries.

## Purpose

This module empowers OpenSPP implementers to extend the platform's data capabilities without requiring technical development. Its primary purposes include:

*   **Tailoring Data Collection:** Enables the creation of specific data points for registrants that go beyond the standard OpenSPP fields, supporting diverse program needs.
*   **User-Friendly Configuration:** Provides an intuitive interface to define and manage custom fields, making it accessible to non-technical users.
*   **Flexible Registrant Profiling:** Allows custom data to be associated with either individual registrants or entire groups, enhancing the detail and relevance of registrant profiles.
*   **Program-Specific Indicators:** Supports the definition of fields for tracking unique program indicators, such as specific beneficiary attributes or eligibility criteria.
*   **Calculated Data Points:** Offers the ability to create fields that automatically calculate values, like counts of specific membership types within a group.

## Dependencies and Integration

The `spp_custom_fields_ui` module integrates with core OpenSPP components to extend their functionality:

*   **Base (`base`)**: As a fundamental Odoo module, `base` provides the underlying data model and user interface framework upon which all OpenSPP modules are built, ensuring standard system operations.
*   **G2P Registry Base (`g2p_registry_base`)**: This module extends the core registrant model, `res.partner`, to manage foundational registrant data. `spp_custom_fields_ui` utilizes this base to add custom fields directly to these established individual and group registrant profiles.
*   **G2P Registry Membership (`g2p_registry_membership`)**: This module defines and manages different types of relationships or roles individuals can have within groups (e.g., Head of Household, Member). `spp_custom_fields_ui` leverages this by allowing custom fields to be specifically associated with or filtered by these membership kinds, enabling highly targeted data collection.

## Additional Functionality

The module introduces several key features for defining and managing custom fields:

### Defining Custom Field Properties

Users can define the core characteristics of each custom field. This includes specifying a clear **Field Draft Name** for easy identification, and determining the **Target Type** to indicate if the field applies to "Group" or "Individual" registrants. The **Field Category** allows distinguishing between "Custom" fields for direct data entry and "Calculated" fields for automatically derived values.

### Tailoring by Membership Kind

A powerful feature allows custom fields to be linked to specific **Kinds** of group membership, as defined in the [G2P Registry Membership](g2p_registry_membership) module. For instance, a custom field might only appear or be relevant for registrants designated as a "Head of Household," enabling highly contextual data collection within groups.

### Presence and Calculated Fields

The module supports creating fields to track **Presence**, which defines a boolean (yes/no) custom field to indicate if a registrant meets a specific condition or possesses an attribute. For "Calculated" fields, the system can automatically generate a field to count occurrences based on specified membership kinds, providing aggregate data without manual calculation.

### Automated Field Naming and Type Assignment

To ensure data consistency and simplify management, the module automatically generates the technical field name based on the defined properties like category, target type, and draft name. Additionally, for "Presence" fields, it automatically assigns a boolean data type, and for other "Calculated" fields, it defaults to an integer type to support counting.

## Conclusion

The OpenSPP Custom Fields UI module is essential for program implementers, providing the flexibility to extend and tailor OpenSPP's data collection capabilities to meet the specific and evolving needs of diverse social protection programs.