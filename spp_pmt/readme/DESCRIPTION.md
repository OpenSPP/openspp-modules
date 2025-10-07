# OpenSPP Pmt

The OpenSPP Pmt module calculates a Proxy Means Testing (PMT) score for groups of registrants. This score helps in identifying and prioritizing beneficiaries for social protection programs, ensuring that assistance reaches those most in need based on objective criteria.

## Purpose

The **OpenSPP Pmt** module provides a robust mechanism for assessing the socio-economic status of registrant groups through a calculated PMT score. This module enables program implementers to make data-driven decisions for beneficiary selection and resource allocation.

Key capabilities include:

*   **Define Custom Field Weights**: Assign numerical weights to specific registrant characteristics (custom fields) that contribute to the PMT score. For example, owning a specific asset might reduce the score, while having a chronic disease might increase it.
*   **Implement Area-Specific Weighting**: Adjust field weights based on geographical location. This allows for nuanced scoring that accounts for variations in living standards and conditions across different areas (e.g., a higher weight for 'access to clean water' in rural areas versus urban areas).
*   **Automate PMT Score Calculation**: Automatically compute a consolidated PMT score for each registrant group by aggregating the weighted values of its individual members' characteristics.
*   **Prioritize Beneficiaries Objectively**: Utilize the calculated PMT score as an objective metric to rank and prioritize groups for enrollment in social protection programs, enhancing fairness and transparency.
*   **Integrate Diverse Indicators**: Incorporate a wide range of individual and household characteristics, such as education levels, health status, and asset ownership, into a single, comprehensive eligibility score.

This module provides the tools to establish transparent and data-informed eligibility criteria, ensuring social protection programs target their intended populations effectively.

## Dependencies and Integration

The **OpenSPP Pmt** module integrates closely with several other core OpenSPP modules to function effectively:

*   **[G2P Registry Base](g2p_registry_base)**: This foundational module provides the core structure for managing individual and group registrant data. The **OpenSPP Pmt** module extends these registrant profiles to store and utilize PMT-specific information and scores.
*   **[G2P Registry Groups](g2p_registry_group)**: As PMT scores are calculated for groups, this module is essential for defining and managing the groups of registrants that will be assessed.
*   **[OpenSPP Custom Filter UI](spp_custom_fields_ui)**: This module allows users to define custom fields for registrants. **OpenSPP Pmt** leverages these custom fields, enabling program implementers to assign weights to them, which are then used in the PMT score calculation.
*   **[OpenSPP Area](spp_area)**: This module manages the hierarchical geographical areas within the system (e.g., country > province > district). **OpenSPP Pmt** uses this area information to apply area-specific weights to custom fields, ensuring PMT calculations reflect local contexts.

The **OpenSPP Pmt** module provides a critical score that can then be used by other modules for targeting, program enrollment, or reporting, acting as a key component in the beneficiary management lifecycle.

## Additional Functionality

The **OpenSPP Pmt** module offers key features to configure and manage the PMT calculation process:

### Configurable Field Weighting

Users can define a default "weight" for any custom field associated with registrants. This weight determines how much a particular characteristic contributes to the overall PMT score. For instance, a field indicating "Has a refrigerator" might be assigned a negative weight to reduce the score, while "Has a chronic illness" might receive a positive weight to increase it.

### Area-Specific Weight Adjustments

Beyond default weights, the module allows for overriding these weights for specific geographical areas. This means a characteristic might have a different impact on the PMT score depending on whether the registrant group resides in "Rural District A" versus "Urban District B." This enables a more accurate assessment that reflects local economic and social realities.

### Automated PMT Score Calculation

The system automatically calculates a PMT score for each registrant group based on the weighted values of its individual members' characteristics. It aggregates these weighted values across all members in a group to produce a single, comprehensive score, providing an objective measure for comparison.

### Integration of Individual Characteristics

The module incorporates specific individual characteristics into the PMT score calculation. These include predefined fields such as "Lower than G.C.E. Ordinary Level," "Currently not attending school or other educational institution," "Long-term (chronic) disease," and "Disability." These boolean (yes/no) indicators, along with custom fields, are weighted and contribute to the group's overall PMT score.

## Conclusion

The **OpenSPP Pmt** module is crucial for OpenSPP, providing the essential capability to objectively calculate Proxy Means Testing scores for registrant groups, thereby streamlining beneficiary identification and ensuring equitable resource allocation in social protection programs.