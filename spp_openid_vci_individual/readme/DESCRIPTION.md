# OpenSPP Openid Vci Individual

The `spp_openid_vci_individual` module extends OpenSPP's Verifiable Credential (VC) issuance capabilities specifically to individual registrants. It enables the secure creation and management of digital proofs of identity and attributes for individuals, leveraging OpenID Connect for Verifiable Presentations (OpenID4VP) and Decentralized Identifiers (DIDs).

## Purpose

This module is designed to empower social protection programs with a robust system for verifiable individual identities. It accomplishes this by:

*   **Enabling Individual VC Issuance:** Facilitates the direct issuance of Verifiable Credentials to individual registrants, linking their verified data to a secure digital format.
*   **Securing Individual Identity:** Provides a cryptographically secure method to represent and verify an individual's identity and specific attributes, enhancing trust and reducing fraud.
*   **Streamlining Issuance Workflows:** Integrates the VC issuance process directly into an individual's profile within the OpenSPP platform, simplifying operations for program staff.
*   **Supporting Verifiable Presentations:** Prepares individual credentials for secure sharing through Verifiable Presentations, allowing individuals to selectively disclose only necessary information.
*   **Tailoring Issuer Configurations:** Allows for the customization and configuration of Verifiable Credential Issuers (VCIs) specifically optimized for individual registrant data and program requirements.

## Dependencies and Integration

The `spp_openid_vci_individual` module acts as a crucial bridge, integrating core VCI functionality with detailed individual registrant data:

*   **[OpenSPP OpenID VCI](spp_openid_vci)**: This module builds upon the foundational capabilities of `spp_openid_vci`, inheriting its core logic for Verifiable Credential issuance, QR code generation, and the user-friendly issuance wizard. It extends these features to apply directly to individual records.
*   **[G2P Registry Individual](g2p_registry_individual)**: It relies on `g2p_registry_individual` to access and utilize the comprehensive data collected for each individual registrant. This ensures that issued VCs accurately reflect verified individual attributes such as names, birthdates, and gender.

By combining these modules, `spp_openid_vci_individual` ensures that VCs issued for individuals are both securely managed and accurately populated with relevant personal data, fitting seamlessly into the overall OpenSPP ecosystem.

## Additional Functionality

This module introduces specific features to enhance the management and issuance of verifiable credentials for individuals:

### Individual-Specific Verifiable Credential Issuance
Users can issue Verifiable Credentials directly from an individual registrant's profile. These VCs encapsulate verified individual data, such as their legal name, date of birth, and program enrollment status, ensuring that all claims are digitally signed and verifiable. This process provides a robust, tamper-evident digital proof of an individual's identity and attributes.

### Integrated QR Code Generation for Individuals
The module automatically generates scannable QR codes for each Verifiable Credential issued to an individual. These QR codes allow for quick and easy verification of an individual's credentials using a mobile device, facilitating both digital and physical proofs of identity, such as on an ID card. This streamlines the process of verifying beneficiary status or identity in various program contexts.

### Customizable VCI Issuer Configuration for Individual Registries
Administrators can define and manage Verifiable Credential Issuers (VCIs) that are specifically tailored for individual registrants. This includes setting up default authentication endpoints and issuer details that align with OpenID Connect standards, ensuring secure and interoperable issuance and presentation of individual-centric credentials. This flexibility supports various program needs and compliance requirements.

## Conclusion

The `spp_openid_vci_individual` module is essential for securely issuing and managing Verifiable Credentials for individual registrants within OpenSPP, enhancing trust, privacy, and efficiency in social protection programs.