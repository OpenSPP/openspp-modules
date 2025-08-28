# OpenSPP Import Dci Api

The `spp_import_dci_api` module integrates OpenSPP with external Digital Civil Identity (DCI) compliant registries, enabling the secure and automated import and synchronization of individual and family registrant data. This module ensures OpenSPP programs have access to current and validated information from authoritative sources.

## Purpose

This module streamlines the process of populating and updating OpenSPP's registrant database, providing a robust bridge to external civil registries. It accomplishes the following key objectives:

*   **Integrate with External Registries**: Establishes secure connections to DCI-compliant external systems, such as national birth or civil registries.
*   **Import and Synchronize Registrant Data**: Fetches and imports individual demographic data, including names, birthdates, gender, and identifiers, ensuring OpenSPP's records are up-to-date.
*   **Automate Registrant Profile Management**: Automatically creates new individual registrant profiles or updates existing ones in OpenSPP based on the imported data, reducing manual data entry and errors.
*   **Manage Hierarchical Location Data**: Imports and structures geographical location data, such as birthplaces, from external sources, allowing for detailed spatial analysis (e.g., country > province > district).
*   **Facilitate Family Group Creation**: Identifies family relationships (e.g., mother-child) from external data and automatically creates corresponding family groups within OpenSPP, improving household-level program targeting.

This module is crucial for maintaining data accuracy and consistency, allowing social protection programs and farmer registries to operate with reliable and current beneficiary information.

## Dependencies and Integration

The `spp_import_dci_api` module builds upon and integrates with several core OpenSPP modules to deliver its functionality:

*   **[OpenSPP Data Source](spp_registry_data_source)**: This foundational module is essential for configuring the connection details, API endpoints, and authentication methods required to communicate with external DCI registries. It defines *how* OpenSPP connects to external systems.
*   **[G2P Registry: Base](g2p_registry_base)**: It extends the core registrant model, using its framework for managing basic registrant data and identification types. Imported individuals and groups are stored within the base registry structure.
*   **[G2P Registry: Individual](g2p_registry_individual)**: This module is extended to store the detailed demographic information of imported individuals, such as names, birthdates, and gender, enriching individual registrant profiles.
*   **[G2P Programs](g2p_programs)** and **[OpenSPP Programs](spp_programs)**: The imported and synchronized registrant data, including individuals and their associated family groups, directly informs program eligibility and entitlement management within these modules. Programs can then leverage this accurate data for beneficiary selection.

## Additional Functionality

The `spp_import_dci_api` module provides a suite of features to manage the import process efficiently:

### External Registry Connection and Search Criteria
Users define specific search criteria to fetch data from external DCI registries. This involves selecting a configured external data source and specifying filters such as birthdate ranges (e.g., "beneficiaries born between 2020-01-01 and 2021-12-31") or specific geographical locations. The module then securely authenticates with the external registry and initiates data retrieval based on these criteria.

### Automated Registrant Import and Updates
Upon successful data retrieval, the module automatically processes individual records. It checks if an individual already exists in OpenSPP using unique identifiers. If a record is new, it creates a complete registrant profile (`res.partner`), including their full name, family name, given name, middle name, gender, and birthdate. If an individual already exists, their profile is updated with the latest information from the DCI registry. The system tracks whether a record was newly created or updated.

### Hierarchical Location Data Management
The module imports and structures geographical data from external registries, such as birthplaces. It maintains a hierarchical structure for locations (e.g., `spp.crvs.location.type` for 'Country', 'Province', 'District', and `spp.crvs.location` for specific instances like 'Philippines', 'Central Luzon', 'Pampanga'). This allows OpenSPP to accurately record and search for registrants based on their geographical attributes.

### Family Group Creation and Relationship Management
The module identifies relationships within the imported data, particularly mother-child links. If a mother and child are imported, it automatically creates or updates a family group (`res.partner` with `is_group=True`) and links both the mother and child to this group using `g2p.group.membership`. This feature also calculates and stores the number of children under 12 months within a family group, enabling programs to target specific household compositions.

## Conclusion

The `spp_import_dci_api` module is a vital component of OpenSPP, enabling efficient, accurate, and automated integration with external civil registries to ensure that social protection programs and farmer registries operate with reliable and current beneficiary data.