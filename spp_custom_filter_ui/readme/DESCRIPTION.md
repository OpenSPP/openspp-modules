# OpenSPP Custom Filter Ui

The OpenSPP Custom Filter UI module customizes the OpenSPP user interface to significantly enhance filtering capabilities for registrant partners (`res.partner` records). This improves usability and efficiency for program managers and administrators in managing individuals and groups within social protection programs and farmer registries.

## Purpose

This module directly addresses the need for efficient data retrieval within OpenSPP, providing program staff with powerful tools to locate and manage registrant information.

*   **Streamlines Data Search**: It enables users to quickly filter `res.partner` records based on a wide array of relevant criteria, from demographics to program enrollment status.
*   **Enhances User Experience**: By making key fields easily filterable, the module reduces the time and effort required to find specific registrants or groups, improving overall productivity.
*   **Supports Program Management**: Program managers can efficiently identify specific populations, such as all registrants in a particular program or all groups of a certain type, for targeted interventions or reporting.
*   **Improves Operational Efficiency**: Faster access to filtered data supports more agile decision-making and more effective management of social protection benefits and farmer registry information.
*   **Customizes UI for Relevance**: It leverages the underlying custom filter mechanism to ensure only the most useful fields are available for filtering, preventing UI clutter and focusing user attention.

## Dependencies and Integration

The `spp_custom_filter_ui` module integrates seamlessly with core OpenSPP functionalities by building upon several foundational modules:

*   **[OpenSPP Custom Filter](spp_custom_filter)**: This module is foundational, providing the core mechanism to define which fields across any model can be made filterable in the user interface. `spp_custom_filter_ui` extends this capability specifically to the `res.partner` model, enabling a tailored set of fields for filtering registrants.
*   **[G2P Registry Groups](g2p_registry_group)**: This module enables the management of groups as registrants and defines various group types. `spp_custom_filter_ui` utilizes this by making the `kind` field (group type) filterable, allowing users to efficiently search for groups based on their classification (e.g., "Household," "Cooperative").
*   **[G2P Programs](g2p_programs)**: This module manages the definition and administration of social protection programs. `spp_custom_filter_ui` enhances the ability to filter `res.partner` records that are often beneficiaries or participants in these programs, improving the management of program-related data for registrants.

This module primarily extends the `res.partner` model, enriching it with the `custom.filter.mixin` to make a comprehensive set of registrant-related fields available for custom filtering throughout OpenSPP's user interface.

## Additional Functionality

The `spp_custom_filter_ui` module significantly expands filtering options for `res.partner` records, allowing users to refine searches based on various criteria.

### Core Registrant and Contact Filters
Users can filter registrants using fundamental contact and status information. This includes filtering by `name`, `address`, `phone`, and `email` for direct contact information. Additionally, the `active` field allows users to quickly view only currently active registrants, streamlining lists and reports.

### Demographic and Personal Identifiers
The module enables detailed searches based on personal attributes. Users can filter by `addl_name` (additional name), `family_name`, and `given_name` for precise identity searches. Filtering by `birth_place`, `birthdate`, and `birthdate_not_exact` helps in identifying individuals based on their birth information, which is crucial for age-based program eligibility.

### Program and Group Affiliation Filters
Program managers can effectively segment registrants based on their roles and associations. Users can filter by `is_registrant` or `is_group` to distinguish between individual beneficiaries and group entities. The `kind` field allows filtering by the type of group (e.g., "Farmer Group," "Household"), while `category_id` helps in classifying registrants further. Filters for `program_membership_ids`, `group_membership_ids`, and `individual_membership_ids` enable identification of registrants based on their participation in specific programs or their relationships within groups.

### Administrative and Audit Trail Filters
This module also provides filters for administrative and system-level data. Users can filter by `registration_date`, `create_date`, `create_uid`, `write_date`, and `write_uid` to track the lifecycle and modification history of registrant records. Filters for `disabled`, `disabled_by`, and `disabled_reason` allow for auditing and managing deactivated registrant accounts, ensuring accountability and data integrity.

## Conclusion

The OpenSPP Custom Filter UI module is essential for enhancing data accessibility and operational efficiency by providing comprehensive and intuitive filtering capabilities for registrant records within OpenSPP.