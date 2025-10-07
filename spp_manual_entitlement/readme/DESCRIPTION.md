# OpenSPP Manual Entitlement

The OpenSPP Manual Entitlement module provides a direct mechanism for administrators to create entitlements for beneficiaries within specific program cycles. This is particularly useful for social protection programs that require flexibility to address unique eligibility criteria, exceptional circumstances, or situations not fully covered by automated entitlement rules.

## Purpose

The OpenSPP Manual Entitlement module accomplishes the following:

*   **Addresses Exceptional Cases**: Allows program managers to manually grant entitlements to beneficiaries who may fall outside standard automated eligibility rules, ensuring no deserving individual is left out. This provides crucial flexibility for dynamic and complex social protection programs.
*   **Ensures Timely Benefit Delivery**: Facilitates the quick setup of entitlements for beneficiaries in situations requiring immediate attention or when automated processes are not yet fully configured, ensuring beneficiaries receive support without delay.
*   **Prevents Duplicate Entitlements**: Includes a check to prevent the creation of duplicate entitlements for a beneficiary within the same program cycle, maintaining data integrity and avoiding overpayments.
*   **Streamlined Entitlement Workflow**: Guides users through a clear, step-by-step wizard to select beneficiaries and confirm entitlement details, simplifying what could otherwise be a complex process.
*   **Scalable Processing**: Supports the efficient creation of entitlements for a large number of beneficiaries through asynchronous processing, preventing system slowdowns and ensuring smooth operations even for extensive programs.

## Dependencies and Integration

The OpenSPP Manual Entitlement module integrates closely with several core OpenSPP components:

-   **Base (base)**: As a foundational Odoo module, 'base' provides the essential technical framework and core functionalities upon which OpenSPP and this module are built.
-   **G2P Registry Base ([g2p_registry_base](g2p_registry_base))**: This module relies on `g2p_registry_base` for access to core registrant data, including beneficiary identities and related information. It ensures that manual entitlements are linked to valid, existing beneficiaries within the system.
-   **G2P Programs ([g2p_programs](g2p_programs))**: `g2p_programs` is central to this module, as it defines program cycles and the overall entitlement management framework. This module extends `g2p_programs` to add the specific capability for manual entitlement creation within defined program cycles.
-   **OpenSPP Registrant Import ([spp_registrant_import](spp_registrant_import))**: While not directly interacting with the manual entitlement process, `spp_registrant_import` plays a role by providing the initial means to bring beneficiary data into the system. This ensures that the beneficiaries available for manual entitlement processing are accurately recorded.

This module extends the `g2p.cycle` and `g2p.program.entitlement.manager.default` models, allowing program cycles to be marked for manual entitlement and providing the specific logic for processing these entitlements. It serves `g2p_programs` by offering an alternative, flexible method for creating entitlements alongside automated processes.

## Additional Functionality

### Manual Entitlement Creation Workflow

Users can initiate the manual entitlement process directly from a program cycle, providing a guided experience. The system presents a list of current cycle members who do not yet have an entitlement, allowing administrators to select specific beneficiaries. This ensures that only relevant individuals are considered for manual intervention.

### Flexible Eligibility and Overrides

This module empowers program managers to grant entitlements to beneficiaries even if they do not meet all automated eligibility criteria. It is designed for situations where human judgment or specific policy exceptions are required, such as a beneficiary who needs immediate support but whose registration is still pending full verification. This capability ensures that programs can adapt to real-world complexities.

### Entitlement Details and Transfer Fee Calculation

When creating a manual entitlement, administrators can define the initial benefit amount for each beneficiary. The module also supports the calculation of transfer fees, which can be configured as either a percentage of the initial amount or a fixed value. These details are then recorded as part of the beneficiary's entitlement, providing transparency and accuracy in benefit disbursement.

### Scalable Asynchronous Processing

For program cycles with a large number of beneficiaries requiring manual entitlements, the module employs asynchronous processing. This means that the system can prepare entitlements in the background without freezing the user interface, ensuring that operations remain smooth and responsive even when dealing with extensive data sets. Users are notified once the entitlement preparation is complete.

## Conclusion

The OpenSPP Manual Entitlement module is a critical component for programs requiring flexibility and human oversight, enabling the precise and efficient allocation of benefits to beneficiaries in exceptional or non-standard circumstances within OpenSPP.