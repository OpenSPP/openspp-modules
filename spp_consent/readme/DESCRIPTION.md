# OpenSPP Consent

The OpenSPP Consent module provides a comprehensive system for managing and tracking explicit consent from individuals and groups within social protection programs and farmer registries. It ensures that all necessary permissions, such as for data collection, program participation, or data sharing, are properly recorded and monitored.

## Purpose

The OpenSPP Consent module enables organizations to effectively manage participant consent, addressing critical requirements for data privacy, program compliance, and ethical data handling. It achieves this by:

*   **Recording Explicit Consent:** Captures and stores specific consent agreements from individuals or groups, detailing what they have consented to.
*   **Associating Consent with Registrants:** Links consent records directly to individual registrants or groups, ensuring clear accountability.
*   **Tracking Consent Validity:** Manages consent records with defined expiry dates, allowing for proactive monitoring and renewal.
*   **Configuring Consent Types:** Allows administrators to define various types of consent, such as "Data Sharing Consent" or "Program Participation Consent," to suit diverse program needs.
*   **Ensuring Compliance:** Provides a structured framework to meet regulatory and ethical requirements for data protection and participant engagement.

## Dependencies and Integration

The OpenSPP Consent module integrates deeply with the core OpenSPP registry modules, leveraging existing registrant structures and extending their capabilities.

*   **[G2P Registry Base](g2p_registry_base)**: This module extends the foundational `res.partner` model, which is used by G2P Registry Base to represent all registrants. Consent records are directly linked to these registrant entities, whether they are individuals or groups.
*   **[G2P Registry Individual](g2p_registry_individual)**: It allows for the recording of consent specifically from individual registrants managed within this module, ensuring that personal data handling is transparent and authorized.
*   **[G2P Registry Group](g2p_registry_group)**: The module supports obtaining and tracking consent from groups, such as households or farmer cooperatives, managed through the G2P Registry Group module. This is vital for programs that operate at a collective level.
*   **[G2P Registry Membership](g2p_registry_membership)**: While not a direct dependency for core functionality, the consent module implicitly supports scenarios where consent might be required for an individual's membership within a group, or for a group's participation in a program.

This module primarily serves other OpenSPP modules by providing a standardized and auditable mechanism for consent management. Any module that collects or processes registrant data can rely on `spp_consent` to ensure that the necessary permissions are in place.

## Additional Functionality

The OpenSPP Consent module offers key features to streamline consent management:

*   **Recording and Tracking Consent**: Users can record new consent agreements for any individual registrant or group. Each consent record captures the specific agreement (e.g., "Consent to share health data") and a mandatory expiry date. This ensures that consent is always time-bound and subject to review or renewal.
*   **Configuring Consent Types**: The module allows administrators to define different types of consent through the 'Consent Configuration' model. This enables flexible categorization of consent requirements, such as "Data Collection Consent" or "Program Benefit Consent," aligning with specific program policies.
*   **Monitoring Expired Consents**: The system provides dedicated views to identify and manage consent records that have expired. This proactive monitoring helps programs ensure ongoing compliance and facilitates timely re-consent processes with registrants.
*   **Integrated Consent Management Workflow**: A user-friendly wizard facilitates the process of recording consent, whether from an individual signatory or on behalf of a group. This ensures consistency and simplifies the data entry process for program staff.

## Conclusion

The OpenSPP Consent module is an essential component of the OpenSPP platform, providing a robust and flexible framework for managing and tracking participant consent. It underpins ethical data practices and ensures program compliance by making consent an integral part of registrant management.