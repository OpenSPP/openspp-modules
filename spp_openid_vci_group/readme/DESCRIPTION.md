# OpenSPP Openid Vci Group

The OpenSPP Openid Vci Group module extends OpenSPP's Verifiable Credential (VC) issuance capabilities to manage and represent groups of registrants. It enables the platform to issue secure, verifiable digital credentials not just for individuals, but for collective entities like households, farmer cooperatives, or community groups, integrating seamlessly with existing group management features.

## Purpose

This module enables OpenSPP to securely represent and verify the identity and attributes of groups. It accomplishes this by:

*   **Issuing Group-Specific Verifiable Credentials:** Generates and issues standardized VCs that encapsulate information about a group, such as its name, type, and registration details, drawn directly from the registry data.
*   **Representing Group Identity:** Provides a verifiable digital identity for groups, allowing them to be recognized and authenticated in various social protection programs or beneficiary registries.
*   **Streamlining Group Verification:** Facilitates the efficient and secure verification of group status and attributes by external entities, reducing manual processes and potential for fraud.
*   **Integrating with Group Management:** Connects the VC issuance process directly with OpenSPP's group management features, ensuring that credentials accurately reflect current group data.
*   **Supporting Diverse Group Types:** Allows VCs to be issued for various types of groups, such as a "Farmer Cooperative" applying for subsidies or a "Household" registering for a social transfer program.

This module is crucial for programs where groups are the primary unit of management or benefit, ensuring their verifiable participation and eligibility.

## Dependencies and Integration

The `spp_openid_vci_group` module builds upon and integrates with key OpenSPP components to deliver its functionality:

*   **[OpenSPP OpenID VCI](spp_openid_vci)**: This is the foundational module for Verifiable Credential issuance. `spp_openid_vci_group` extends its core capabilities, adapting the VC generation and management framework to specifically handle group entities.
*   **[G2P Registry Groups](g2p_registry_group)**: This module provides the framework for defining, creating, and managing different types of groups within OpenSPP. `spp_openid_vci_group` leverages the group data and structures established by `g2p_registry_group` to populate the claims within group-specific VCs.
*   **[G2P Registry Base](g2p_registry_base)**: While not a direct dependency, `g2p_registry_group` relies on `g2p_registry_base` for its core registrant features. Consequently, `spp_openid_vci_group` indirectly benefits from the foundational data model that allows groups to be treated as a type of registrant.

This integration ensures that group VCs are issued consistently with individual VCs and draw from the authoritative group data maintained in the system.

## Additional Functionality

This module introduces specific features to enable robust Verifiable Credential issuance for groups:

### Group-Specific Credential Types
The module introduces a dedicated "GroupRegistry" credential type within the VCI issuer configuration. This allows administrators to define unique schemas and data requirements for group credentials, ensuring that the issued VCs accurately reflect relevant group attributes and comply with specific program needs. For example, a VC for a farmer group might include its registration number and primary crop.

### Tailored Issuance Process for Groups
It adapts the existing VC issuance wizard to streamline the process for groups. Users can select a group and initiate the credential issuance, with the system automatically extracting and preparing the relevant group data for inclusion in the Verifiable Credential. This ensures a consistent and user-friendly experience for both individual and group VC issuance.

### Secure Representation of Group Attributes
This module enables the secure digital representation of a group's verifiable attributes. Once issued, the VC serves as a tamper-evident digital proof of the group's identity and specific characteristics, such as its legal status, membership count, or operational area (e.g., "Province > District > Village"). This allows for quick and reliable verification by authorized parties.

### Integration with Group Data Models
The module seamlessly integrates with the group data models provided by the [G2P Registry: Groups](g2p_registry_group) module. When issuing a credential, it automatically retrieves and populates the VC with accurate information about the group, such as its name, type, and any associated identifiers, ensuring data consistency and reducing manual data entry.

## Conclusion

The `spp_openid_vci_group` module is vital for extending OpenSPP's Verifiable Credential capabilities to groups, enabling secure digital identity and attribute verification for collective entities in social protection and registry programs. It ensures that group management is fully integrated with a robust and modern credentialing system.