# OpenSPP Openid Vci

The `spp_openid_vci` module empowers the OpenSPP platform to issue and manage Verifiable Credentials (VCs) for program registrants. It leverages OpenID Connect for Verifiable Presentations (OpenID4VP) to provide secure, tamper-proof digital proofs of identity and program eligibility.

## Purpose

This module equips OpenSPP with the capability to provide registrants with trusted digital credentials, streamlining verification processes and enhancing data security. It addresses the need for secure, standardized, and easily verifiable digital proofs within social protection programs.

Key capabilities include:

-   **Issue Verifiable Credentials (VCs):** Generate and issue secure digital credentials to individual registrants, representing claims about their identity or program eligibility.
-   **Generate VC QR Codes:** Automatically create QR codes for each issued VC, enabling quick and secure digital sharing and verification by authorized parties.
-   **Secure Credential Management:** Ensure the authenticity and integrity of VCs through robust digital signing and encryption, preventing tampering and fraud.
-   **Integrate Registrant Data:** Seamlessly pull and incorporate relevant registrant data from the core OpenSPP registry into issued VCs.
-   **Support Physical ID Cards:** Facilitate the printing of physical ID cards that include the digital VC QR code, bridging the gap between physical and digital identity.

This module's value lies in its ability to empower registrants with portable, verifiable digital identities, reducing administrative burdens and improving the efficiency and trustworthiness of social protection program operations. For example, a registrant can present a digital VC (via QR code) to prove eligibility for a food assistance program without needing physical documents.

## Dependencies and Integration

The `spp_openid_vci` module is a crucial component that builds upon and extends several core OpenSPP modules to deliver comprehensive verifiable credential functionality.

-   **[G2P OpenID VCI](g2p_openid_vci):** This module directly extends the core `g2p_openid_vci` module, inheriting its foundational logic for defining VCI issuers, credential types, and the underlying mechanisms for credential generation.
-   **[G2P Openid Vci Rest Api](g2p_openid_vci_rest_api):** It integrates with this module to ensure that the credential issuance capabilities are exposed through a standardized RESTful API, allowing external digital wallets and applications to securely request and receive VCs.
-   **[OpenSPP Encryption Module](spp_encryption) and [G2P Encryption REST API](g2p_encryption_rest_api):** `spp_openid_vci` relies on these modules to perform the cryptographic signing and encryption of Verifiable Credentials. This ensures the integrity, authenticity, and confidentiality of the issued VCs.
-   **[G2P Registry Base](g2p_registry_base):** This module sources registrant data from `g2p_registry_base` (specifically `res.partner` records) to populate the claims within the Verifiable Credentials. It ensures VCs accurately reflect registered identities and attributes.
-   **[OpenSPP User Roles](spp_user_roles):** It integrates with `spp_user_roles` to manage and restrict user permissions for issuing VCs and configuring related settings, ensuring that only authorized personnel can perform these sensitive operations.

Together, these modules form a robust ecosystem where registrant data is securely transformed into verifiable digital credentials, accessible both within OpenSPP and to authorized external systems.

## Additional Functionality

The `spp_openid_vci` module introduces several key features to manage and issue verifiable credentials effectively.

### Streamlined Verifiable Credential Issuance

This module enables users to easily issue Verifiable Credentials (VCs) to individual registrants. The process links a registrant's unique identifier (e.g., National ID) with a configured VCI issuer, ensuring that the issued credential is tied to a verified identity. Upon successful issuance, the system generates the digital VC, containing relevant registrant data and secured by cryptographic signatures.

### Automatic VC QR Code Generation

For every Verifiable Credential issued, the module automatically generates a corresponding QR code. This QR code encapsulates the digital VC, making it highly portable and easy to share. The generated QR code is stored directly on the registrant's record, allowing for quick retrieval and presentation, for instance, during field verification or program access.

### Integrated ID Card Printing

The module facilitates the printing of physical ID cards that incorporate the digital Verifiable Credential. Each printed ID card includes the VC QR code, effectively bridging the gap between physical and digital identity. This feature ensures that registrants have a tangible proof of identity or eligibility while also carrying a digitally verifiable credential for enhanced security and convenience.

### Enhanced Issuer Configuration and Security

The module extends the core VCI issuer management to allow for more flexible configuration. It automatically retrieves public keys (JWKS) from all configured encryption providers, ensuring broader interoperability for verifying credentials. This enhancement strengthens the security posture and flexibility of the VCI system.

## Conclusion

The `spp_openid_vci` module is essential for empowering OpenSPP with robust, secure digital credentialing capabilities, enabling efficient and trustworthy verification of registrant identities and program eligibility.