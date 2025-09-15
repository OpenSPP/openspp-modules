# OpenSPP Programs Compliance Criteria

The 'OpenSPP Programs Compliance Criteria' module enhances OpenSPP's social protection program management by enabling administrators to define, manage, and enforce additional eligibility and compliance requirements for beneficiaries beyond initial program enrollment criteria. This ensures ongoing adherence to program rules and accurate beneficiary targeting.

## Purpose

This module significantly strengthens program integrity and beneficiary management by:

*   **Defining Flexible Compliance Rules**: Administrators can establish specific, dynamic criteria that beneficiaries must meet to remain compliant with program requirements. These rules can be tailored to individual programs.
*   **Automating Compliance Checks**: It automates the process of evaluating beneficiaries against defined compliance criteria within program cycles, streamlining program operations.
*   **Identifying Non-Compliant Beneficiaries**: The module clearly flags beneficiaries who fail to meet the ongoing compliance criteria, changing their status to 'Non-Compliant'.
*   **Enhancing Program Accountability**: By enforcing additional rules, the module helps ensure that benefits are consistently directed to the intended and deserving populations.
*   **Configuring Filtering Mechanisms**: Program managers can choose when compliance filtering is applied, such as upon membership creation or entitlement generation, offering operational flexibility.

The module ensures programs maintain their intended focus and resource allocation by continuously verifying beneficiary eligibility and compliance throughout a program's lifecycle. For example, a program might require beneficiaries to attend school regularly or reside within a specific administrative area (e.g., country > province > district).

## Dependencies and Integration

The 'OpenSPP Programs Compliance Criteria' module integrates deeply with core OpenSPP components to extend program management capabilities:

*   **[G2P Registry Base](g2p_registry_base)**: It leverages the foundational registrant data from this module to evaluate compliance criteria, using information like demographics, relationships, and identification details.
*   **[G2P Programs](g2p_programs)**: This module extends the core `g2p.program` and `g2p.cycle` models, allowing program managers to define compliance rules directly within program configurations and apply these rules to program cycles.
*   **[OpenSPP Area](spp_area)**: Compliance criteria can incorporate geographical constraints, utilizing the hierarchical area data managed by this module to define rules based on a beneficiary's administrative location.
*   **[OpenSPP Programs](spp_programs)**: It builds upon the enhanced program features of OpenSPP Programs, providing additional layers of control and verification for both cash and in-kind entitlement programs.

## Additional Functionality

### Defining Program-Specific Compliance Rules

This module allows program administrators to establish detailed compliance criteria unique to each social protection program.

*   **Customizable Criteria**: Administrators can define flexible rules using domain expressions, allowing for complex conditions based on any beneficiary data available in the system.
*   **Geographical Scope**: Compliance criteria can be tied to specific administrative areas, ensuring beneficiaries meet location-based requirements.
*   **Integration with Program Creation**: When creating a new program, administrators can immediately enable and configure initial compliance criteria through a dedicated wizard.

### Automating Compliance Checks

The module provides tools to automatically evaluate beneficiary compliance within active program cycles.

*   **One-Click Filtering**: Within a program cycle, users can trigger a compliance check that evaluates all enrolled beneficiaries against the defined criteria.
*   **Automated State Transition**: Beneficiaries found not to meet the criteria are automatically marked with a 'Non-Compliant' status, streamlining the identification process.
*   **Configurable Automation**: System administrators can configure the system to automatically apply compliance filtering at specific events, such as when new cycle memberships are created or when entitlements are generated.

### Monitoring Beneficiary Compliance Status

The module provides clear visibility into the compliance status of all program beneficiaries.

*   **New 'Non-Compliant' Status**: A dedicated 'Non-Compliant' state is added to beneficiary cycle memberships, making it easy to identify beneficiaries requiring attention.
*   **Comprehensive Enrollment Counts**: Program cycles display the total number of enrollments, providing a complete overview of all beneficiaries, regardless of their compliance status. This allows for both filtered and unfiltered views of program participation.

## Conclusion

The 'OpenSPP Programs Compliance Criteria' module is essential for maintaining the integrity and effectiveness of social protection programs by providing robust tools for defining, automating, and monitoring beneficiary adherence to program rules. It ensures that OpenSPP programs consistently serve their intended populations through flexible and enforceable compliance management.