# OpenSPP Dci Api Server

The OpenSPP DCI API Server module provides a secure, standardized interface for external systems to access and exchange registry data with OpenSPP. It acts as a bridge, enabling interoperability and data sharing in a consistent, DCI-compliant format.

## Purpose

This module establishes a robust and secure mechanism for data exchange, essential for integrated social protection programs. It accomplishes the following key capabilities:

*   **Exposes Registry Data:** It provides a RESTful API to securely access OpenSPP's comprehensive individual and household registry data, formatted according to DCI standards.
*   **Enables Secure Integration:** The module ensures that data exchange with external applications is secure through client credential management and token-based authentication.
*   **Facilitates Interoperability:** By adhering to DCI (Digital Cash Initiative or similar standard implied by context) standards, it allows OpenSPP to seamlessly integrate with other social protection platforms and data consumers.
*   **Manages API Client Access:** It provides tools to create and manage credentials for external systems or applications that need to interact with the OpenSPP registry API.
*   **Generates Access Tokens:** Authorized clients can obtain temporary access tokens, ensuring controlled and time-limited access to sensitive registry information.

This module's value lies in its ability to unlock OpenSPP's registry data for broader use, supporting initiatives like sharing beneficiary information with other government agencies or integrating with external mobile data collection applications, all while maintaining strict security and data integrity.

## Dependencies and Integration

The `spp_dci_api_server` module integrates deeply with several core OpenSPP modules to function effectively:

*   **[G2P Registry: Base](g2p_registry_base)**: This foundational module provides the core registrant structure and management, on which the DCI API builds its data exposure.
*   **[G2P Registry: Individual](g2p_registry_individual)**: It relies on this module for detailed individual registrant profiles, including names, birthdates, and gender, which are exposed through the API.
*   **[G2P Registry: Group](g2p_registry_group)**: This module supplies the group (e.g., household) information that is often associated with individuals and made available via the API.
*   **[G2P Registry: Membership](g2p_registry_membership)**: It leverages this module to retrieve and present the relationships between individuals and groups, such as household memberships.
*   **[OpenSPP API: Oauth](spp_oauth)**: Crucially, the DCI API Server utilizes `spp_oauth` to provide robust authentication and authorization, ensuring that only authenticated clients can access its endpoints and generate tokens.

## Additional Functionality

### Secure API Client Credential Management

Users can create and manage dedicated credentials for each external application or system that needs to connect to the DCI API. For each new API client, the system automatically generates a unique **Client ID** and **Client Secret**, which are essential for authentication. For security, these credentials can only be viewed once upon creation. Each API client is identified by a unique **Client Name**.

### DCI-Compliant Registry Data Exposure

This module exposes a comprehensive set of individual and household registry data through its API, formatted to align with DCI standards. External systems can retrieve detailed individual profiles, including unique identifiers, given and family names, birthdate, gender, birth place, email, and phone numbers. It also includes associated household information, such as household name, identifiers, and phone numbers, for each individual's group memberships.

### Dynamic Access Token Generation

Authorized API clients use their Client ID and Client Secret to request and receive temporary access tokens. These tokens, generated as JSON Web Tokens (JWTs), grant time-limited access to the DCI API endpoints, enhancing security by ensuring that access is not perpetual. The expiration time for these tokens is configurable, allowing administrators to define the duration of valid access.

## Conclusion

The OpenSPP DCI API Server module is fundamental to OpenSPP's ecosystem, providing a secure and standardized gateway for external systems to access and utilize critical social protection registry data, thereby enhancing interoperability and collaborative program management.