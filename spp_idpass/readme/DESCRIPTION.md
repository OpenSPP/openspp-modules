# OpenSPP Idpass

The OpenSPP Idpass module (technical name: spp_idpass) provides OpenSPP with the capability to securely generate and manage digital identification passes for program registrants, streamlining beneficiary verification and access to social protection services.

## Purpose

The OpenSPP Idpass module enables efficient and reliable identification of beneficiaries and groups through several key capabilities:

*   **Automated ID Generation**: It automatically generates printable ID passes for individuals and groups by leveraging existing registrant data within OpenSPP. This reduces manual effort and ensures consistent identification documents.
*   **Configurable ID Templates**: Administrators can define and manage multiple ID pass templates, each with customizable expiry rules and specific configurations for integration with external ID generation services. This offers flexibility for different program requirements.
*   **Secure External Integration**: The module integrates with external ID generation services through secure API calls, allowing OpenSPP to utilize specialized services for producing high-quality digital IDs. This ensures data security and leverages advanced features.
*   **Centralized ID Management**: Once generated, the ID pass is stored as a digital file on the registrant's record, and their identification profile is updated. This provides a centralized and verifiable source of identification for beneficiaries.
*   **Group ID Issuance**: It supports issuing ID passes for groups, automatically identifying the principal recipient or head of the group to ensure accurate representation on the ID document.

## Dependencies and Integration

The OpenSPP Idpass module seamlessly integrates with core OpenSPP components and other registry modules:

*   It extends the `res.partner` model (from the `base` module and further enhanced by [G2P Registry Base](g2p_registry_base)) to store the generated ID pass file and its filename directly on the registrant's profile. This allows for quick access and management of the digital ID.
*   The module relies heavily on the registrant data managed by [G2P Registry Base](g2p_registry_base), utilizing fields such as given names, family names, birth details, and gender to populate the ID pass. It also integrates with the `g2p.id.type` model to categorize the generated ID pass as a specific type of identification and with `g2p.reg.id` to record the issued ID number.
*   When issuing ID passes for groups, OpenSPP Idpass leverages the definitions and relationships established within the [G2P Registry Membership](g2p_registry_membership) module to correctly identify the designated "Head" or "Principal Recipient" whose details will appear on the group's ID.

## Additional Functionality

### ID Pass Template Configuration

Users can define and manage various "ID Pass Templates" within the module, allowing for flexible ID generation. Each template specifies:
*   An external API endpoint and authentication credentials (username, password) for secure communication with an ID generation service.
*   An optional authentication token URL to generate temporary access tokens, enhancing security.
*   The ID's expiry length (e.g., 1 year, 6 months, or 30 days) and a unique filename prefix for generated PDF documents.
Templates can be activated or deactivated, providing administrators with control over which ID generation sources are currently in use.

### Automated ID Issuance for Registrants

From a registrant's profile, users can initiate a dedicated "Issue ID Pass" wizard. The system automatically gathers relevant registrant data (such as names, birth information, gender, and profile picture) and securely transmits it to the configured external ID generation service. For groups, the module intelligently identifies the designated "Head" or "Principal Recipient" using data from the [G2P Registry Membership](g2p_registry_membership) module, ensuring their details are correctly used for the ID. Upon successful generation, the module stores the ID pass PDF directly on the registrant's record and updates their official `g2p.reg.id` with the new ID number.

### Protected Default ID Type

The module introduces a default "ID Pass" type within the `g2p.id.type` framework. This specific ID type is protected from accidental deletion or modification by users, ensuring that the core functionality for ID Pass generation remains stable and available for all programs. This prevents critical system configurations from being inadvertently altered.

### Secure API Communication

The OpenSPP Idpass module handles all secure communication with external ID generation APIs. It includes functionality to generate authentication tokens when required by the external service, using the provided credentials, and incorporates robust error handling to provide clear messages if the external service encounters issues. All API requests include timeouts to prevent system hangs, ensuring reliable operation.

## Conclusion

The OpenSPP Idpass module centralizes and automates the secure generation and management of digital identification passes, streamlining beneficiary identification and enhancing program delivery across social protection initiatives.