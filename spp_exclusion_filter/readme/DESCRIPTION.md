# OpenSPP Exclusion Filter

The OpenSPP Exclusion Filter module streamlines the program creation process by enabling administrators to define and apply specific criteria to exclude ineligible registrants. This ensures that only qualified individuals are considered for enrollment in social protection programs, enhancing efficiency and program integrity.

## Purpose

This module provides a robust mechanism to manage and apply exclusion rules, ensuring that program benefits reach the intended beneficiaries. It accomplishes this by:

*   **Defining Exclusion Criteria**: Users can establish clear, configurable rules based on various registrant attributes or existing program participation to identify individuals who should not be enrolled.
*   **Automating Eligibility Checks**: During program setup, the module automatically applies these pre-defined filters, significantly reducing manual effort and the risk of errors in beneficiary selection.
*   **Enhancing Program Integrity**: By systematically excluding ineligible registrants, the module helps prevent fraud, double-dipping, and ensures compliance with program guidelines.
*   **Streamlining Enrollment**: It refines the pool of potential beneficiaries early in the program creation workflow, allowing program managers to focus on truly eligible candidates.
*   **Supporting Fair Distribution**: The module ensures that resources are allocated equitably by preventing individuals who do not meet specific requirements, or who are already receiving similar benefits, from being considered.

For instance, an exclusion filter could prevent registrants already enrolled in a specific cash transfer program from being considered for a new, similar program, or exclude individuals above a certain income threshold.

## Dependencies and Integration

The OpenSPP Exclusion Filter module integrates seamlessly with core OpenSPP components, extending their functionality to incorporate advanced eligibility management.

*   **Base (base)**: Provides the foundational Odoo framework, enabling core user interface elements and data management capabilities for the module.
*   **G2P Registry Base ([g2p_registry_base](g2p_registry_base))**: Leverages the core registrant data managed by the registry, allowing exclusion filters to be built upon and applied to comprehensive registrant profiles.
*   **G2P Programs ([g2p_programs](g2p_programs))**: Builds upon the core program definition and management features, enhancing the program creation workflow by introducing a critical step for applying exclusion criteria.
*   **OpenSPP Programs ([spp_programs](spp_programs))**: Extends the OpenSPP-specific program functionalities, ensuring that exclusion filters can be configured and utilized within the broader context of OpenSPP's social protection programs.

This module primarily serves `g2p_programs` and `spp_programs` by providing an essential layer of control during the program creation and beneficiary selection phases.

## Additional Functionality

The module introduces key features to define and apply exclusion criteria effectively within OpenSPP programs.

### Configuring Exclusion Rules

Users gain access to an Eligibility Manager where they can define and manage various exclusion criteria. These rules specify the conditions under which a registrant should be deemed ineligible for a program. For example, a rule might exclude registrants who are already beneficiaries of "Program X" or those whose household income exceeds a defined threshold. Administrators can create new rules, modify existing ones, and activate or deactivate them as program requirements evolve.

### Applying Filters During Program Creation

During the program creation wizard, administrators can select and apply one or more pre-configured exclusion filters. This crucial step integrates the exclusion logic directly into the program setup process. Once selected, the module automatically processes the potential beneficiary pool against these filters, generating a refined list of truly eligible registrants. This ensures that the initial program enrollment considers only those who meet all inclusion criteria and none of the exclusion criteria.

### Automated Registrant Screening

The module automates the process of screening registrants against the defined exclusion rules. When a filter is applied, the system identifies and flags any registrant who meets the exclusion conditions. This automated screening significantly reduces the administrative burden of manual eligibility checks, minimizes human error, and ensures consistent application of program rules across all registrants.

## Conclusion

The OpenSPP Exclusion Filter module is vital for maintaining the integrity and efficiency of social protection programs by enabling precise control over beneficiary eligibility and streamlining the program enrollment process.