# OpenSPP Base

The OpenSPP Base module (`spp_base`) is the foundational component of the OpenSPP platform. It provides the essential configurations, core functionalities, and user interface customizations necessary for managing social protection programs and farmer registries. This module establishes the common building blocks upon which other OpenSPP modules operate, ensuring data consistency and a streamlined user experience across the system.

## Purpose

The OpenSPP Base module establishes the core framework and essential capabilities for the entire platform. It ensures a consistent and robust environment for managing program data.

*   **System Foundation**: Establishes core system settings and a mechanism for generating unique identifiers for various records. This ensures consistent data tracking and integrity across all OpenSPP modules.
*   **Enhanced Registrant Profiles**: Extends the base registrant model to include additional, critical information such as registrant tags, gender details, and a clear distinction of registrant type (e.g., individual, group). This enables more comprehensive data capture and analysis for beneficiaries.
*   **Top-up Card Management**: Supports the integration and validation of Top-up Cards as a specific form of identification within the system. This is crucial for programs utilizing physical cards for beneficiary interactions.
*   **Core UI and Role Configuration**: Provides fundamental user interface elements and initial security configurations, including global and local user roles. This ensures a consistent look and feel and lays the groundwork for robust access control.
*   **Integration Enabler**: Serves as a central integration point, allowing other OpenSPP modules to seamlessly interact with core registrant data and system settings.

## Dependencies and Integration

The OpenSPP Base module is deeply integrated into the OpenSPP ecosystem, extending core functionalities and serving as a prerequisite for many other modules.

*   It extends the core G2P Registry models, including `res.partner` (registrants), `g2p.reg.id` (registrant IDs), and `g2p.group.membership` (group memberships) from [G2P Registry Base](g2p_registry_base), [G2P Registry Individual](g2p_registry_individual), and [G2P Registry Group](g2p_registry_group). This provides foundational data structures for all registrants.
*   This module integrates with geographical and service delivery modules like [OpenSPP Area](spp_area) and [OpenSPP Service Points](spp_service_points) by providing the underlying registrant framework and unique identifiers used across the system.
*   It supports identity management features such as [spp_idpass](spp_idpass) and [spp_idqueue](spp_idqueue) by defining the 'Top-up Card' ID type and its validation rules, crucial for card issuance and tracking.
*   OpenSPP Base underpins UI customization and filtering through [OpenSPP Custom Field](spp_custom_field), [OpenSPP Custom Fields UI](spp_custom_fields_ui), [OpenSPP Hide Menus](spp_hide_menus), and [OpenSPP Custom Filter UI](spp_custom_filter_ui), establishing common interface elements and simplifying user workflows.
*   It defines global and local roles, which are utilized by [OpenSPP User Roles](spp_user_roles) to manage permissions and access control for users based on their responsibilities and assigned areas.

## Additional Functionality

The OpenSPP Base module delivers several key features that enhance the core functionality and user experience of the OpenSPP platform.

### Unique Identifier Management

The module provides a robust system for generating unique identifiers for various records within OpenSPP. These identifiers are automatically assigned and validated, following specific patterns to ensure consistency and prevent errors. This capability is crucial for accurately tracking beneficiaries, programs, and other entities across different modules and activities.

### Enhanced Registrant Profiles

It extends the core registrant profile by adding critical fields for more comprehensive data capture. Users can assign multiple `Registrant Tags` for flexible categorization and reporting, and easily see the `String Kind` of a registrant (e.g., individual, household). This module also integrates `Gender` information into individual and group membership records, allowing for more detailed demographic analysis of beneficiary populations.

### Top-Up Card Identification

OpenSPP Base manages the specific `Top-up Card` identification type, including its unique identifier (`Card UID`). The system ensures data accuracy by validating that all entered Top-up Card UIDs are exactly 10 characters long. This standardization is essential for reliable card issuance, tracking, and usage in program distributions.

### Foundational UI and Role Configuration

This module establishes the fundamental user interface components and initial security settings for the OpenSPP platform. It pre-defines `Global Roles` and `Local Roles` to streamline user permission management and sets up the basic views for interacting with registrants and user accounts. This ensures a secure, consistent, and user-friendly operating environment from the outset.

## Conclusion

The OpenSPP Base module serves as the foundational layer of the OpenSPP platform, providing essential data structures, core functionalities, and UI configurations that enable robust social protection program management.