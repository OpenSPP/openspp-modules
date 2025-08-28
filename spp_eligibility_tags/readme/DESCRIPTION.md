# OpenSPP Eligibility Tags

The OpenSPP Eligibility Tags module provides a robust mechanism for defining and managing program eligibility criteria based on registrant tags and geographical areas. It automates the identification of beneficiaries, significantly improving the accuracy and efficiency of program targeting.

## Purpose

This module streamlines the process of identifying eligible program beneficiaries by:

*   **Defining Eligibility by Registrant Tags**: Allows program administrators to specify eligibility using pre-defined registrant tags, ensuring that only individuals or groups with relevant characteristics are considered.
*   **Enabling Geographical Targeting**: Restricts eligibility to specific administrative areas, such as a country, province, or district, ensuring programs reach their intended geographical scope.
*   **Automating Beneficiary Identification**: Automatically generates a dynamic list of eligible registrants by combining selected tags and geographical areas, removing manual verification.
*   **Improving Targeting Accuracy**: Enhances the precision of beneficiary selection, reducing errors and ensuring program resources are directed to the most appropriate recipients.
*   **Facilitating Efficient Enrollment**: Supports the quick and accurate enrollment of identified eligible registrants into social protection programs, even for large populations.

## Dependencies and Integration

The OpenSPP Eligibility Tags module integrates seamlessly with core OpenSPP components and extends existing functionalities:

*   **Base (base)**: Provides foundational Odoo features necessary for module operation.
*   **G2P Registry Base (g2p_registry_base)**: Leverages the core registrant data, including the ability to assign custom tags to registrants and define geographical areas. This module builds upon these foundational data structures to create eligibility rules.
*   **G2P Programs (g2p_programs)**: Extends the general `g2p.eligibility.manager` by introducing "Tag-based Eligibility" as a new, specific method for determining program eligibility. This allows program managers to select this module's approach when setting up a program.
*   **OpenSPP Programs (spp_programs)**: Enhances the OpenSPP-specific program management by providing a specialized eligibility calculation method that considers both registrant tags and geographical locations.

## Additional Functionality

The spp_eligibility_tags module introduces key features for precise beneficiary targeting:

### Defining Tag-Based Eligibility

Users can select specific registrant tags to define eligibility criteria for a program. For example, a program might target "Vulnerable Households" or "Farmers in Drought-Affected Areas" by simply selecting the corresponding tags already assigned to registrants. This allows for flexible and dynamic categorization of beneficiaries.

### Geographical Area Targeting

Beyond tags, the module enables administrators to narrow eligibility to specific geographical areas. Users can select an administrative area (e.g., a specific district, province, or country) to ensure that only registrants residing within that defined boundary are considered eligible. This is crucial for localized social protection interventions.

### Automated Eligibility Assessment

Based on the selected tags and geographical area, the module automatically constructs a dynamic search domain to identify all matching registrants. This domain is continuously updated, ensuring that the list of eligible individuals or groups remains accurate as registrant data or program criteria evolve.

### Efficient Beneficiary Enrollment

Once eligibility criteria are set, users can initiate the enrollment of all identified eligible registrants into the program. For programs with a large number of potential beneficiaries, the module uses asynchronous processing to import registrants efficiently without impacting system performance, providing updates on the import progress.

```{note}
For very large beneficiary populations, the system intelligently queues import jobs to ensure smooth operation and provide administrators with progress updates.
```

## Conclusion

The OpenSPP Eligibility Tags module is a vital component for OpenSPP programs, enabling precise, automated, and scalable identification of beneficiaries through flexible tag and geographical area-based eligibility criteria.