OpenSPP IDPASS
==============

The OpenSPP Idpass module (technical name: ``spp_idpass``) provides OpenSPP with the capability to securely generate and manage digital identification passes for program registrants, streamlining beneficiary verification and access to social protection services.

Purpose
-------

The OpenSPP Idpass module enables efficient and reliable identification of beneficiaries and groups through several key capabilities:

- Automated ID Generation: automatically generates printable ID passes for individuals and groups by leveraging existing registrant data within OpenSPP. This reduces manual effort and ensures consistent identification documents.
- Configurable ID Templates: administrators can define and manage multiple ID pass templates, each with customizable expiry rules and specific configurations for integration with external ID generation services. This offers flexibility for different program requirements.
- Secure External Integration: integrates with external ID generation services through secure API calls, allowing OpenSPP to utilize specialized services for producing high-quality digital IDs, while ensuring data security.
- Centralized ID Management: once generated, the ID pass is stored as a digital file on the registrant's record, and their identification profile is updated. This provides a centralized and verifiable source of identification for beneficiaries.
- Group ID Issuance: supports issuing ID passes for groups, automatically identifying the principal recipient or head of the group to ensure accurate representation on the ID document.

Dependencies and Integration
----------------------------

The module integrates with core OpenSPP components and other registry modules:

- Extends the ``res.partner`` model (from the ``base`` module and further enhanced by G2P Registry Base) to store the generated ID pass file and its filename directly on the registrant's profile.
- Leverages registrant data managed by G2P Registry Base to populate the ID pass (names, birth details, gender) and integrates with ``g2p.id.type`` to categorize the generated ID pass as a specific type of identification and with ``g2p.reg.id`` to record the issued ID number.
- For group IDs, uses relationships from the G2P Registry Membership module to correctly identify the "Head" or "Principal Recipient" whose details will appear on the group's ID.

Additional Functionality
------------------------

ID Pass Template Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users can define and manage various "ID Pass Templates" within the module, allowing for flexible ID generation. Each template specifies:

- An external API endpoint and authentication credentials (username, password) for secure communication with an ID generation service.
- An optional authentication token URL to generate temporary access tokens, enhancing security.
- The ID's expiry length (for example, 1 year, 6 months, or 30 days) and a unique filename prefix for generated PDF documents.

Templates can be activated or deactivated to control which ID generation sources are currently in use.

Automated ID Issuance for Registrants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From a registrant's profile, users can initiate an "Issue ID Pass" wizard. The system automatically gathers relevant registrant data (such as names, birth information, gender, and profile picture) and securely transmits it to the configured external ID generation service.

For groups, the module identifies the designated "Head" or "Principal Recipient" using data from the G2P Registry Membership module, ensuring their details are correctly used for the ID. Upon successful generation, the module stores the ID pass PDF directly on the registrant's record and updates their official ``g2p.reg.id`` with the new ID number.

Protected Default ID Type
~~~~~~~~~~~~~~~~~~~~~~~~~

The module introduces a default "ID Pass" type within the ``g2p.id.type`` framework. This specific ID type is protected from accidental deletion or modification by users, ensuring that the core functionality for ID Pass generation remains stable and available for all programs.

Secure API Communication
~~~~~~~~~~~~~~~~~~~~~~~~

All communication with external ID generation APIs is handled securely. When required by the external service, the module can generate authentication tokens using the provided credentials. Robust error handling provides clear messages if the external service encounters issues, and all API requests include timeouts to prevent hangs.

Conclusion
----------

The OpenSPP Idpass module centralizes and automates the secure generation and management of digital identification passes, streamlining beneficiary identification and enhancing program delivery across social protection initiatives.

