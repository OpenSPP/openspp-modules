# OpenSPP Change Request Add Children Demo

This module provides a demonstration of how OpenSPP manages the process of adding new children or members to an existing group within the registry. It integrates a dedicated form, ID scanning capabilities, and automated data updates through the OpenSPP Change Request framework, ensuring a structured and auditable process.

## Purpose

The 'spp_change_request_add_children_demo' module streamlines the expansion of group registries by enabling the efficient and accurate addition of new members. It accomplishes this by:

*   **Standardizing Member Addition**: Establishes a formal Change Request process for adding new individuals to existing groups, such as adding a child to a household or a farmer to a cooperative.
*   **Integrating ID Scanning**: Facilitates rapid data entry by allowing the scanning of identification documents to automatically populate registrant details.
*   **Automating Data Updates**: Upon approval, automatically creates new individual registrant profiles and updates the target group's membership records.
*   **Ensuring Data Quality**: Implements robust validation rules for critical data fields like birthdate, phone numbers, and unique identification numbers.
*   **Documenting Supporting Evidence**: Manages the secure storage of all supporting documents, such as scanned IDs, within the system's Document Management System (DMS).

This module empowers program staff to manage group composition changes effectively, reducing manual errors and maintaining high data integrity for social protection programs and farmer registries.

## Dependencies and Integration

This module seamlessly integrates with core OpenSPP components and extends the Change Request framework to handle specific group membership updates:

*   **[OpenSPP Base](spp_base)**: Provides foundational OpenSPP functionalities and configurations necessary for the module's operation.
*   **[OpenSPP Change Request](spp_change_request)**: Serves as the primary framework, enabling this module to define a specific type of change request for adding members and leverage its multi-stage approval workflow.
*   **[G2P Registry Base](g2p_registry_base)**, **[G2P Registry Individual](g2p_registry_individual)**, **[G2P Registry Group](g2p_registry_group)**, **[G2P Registry Membership](g2p_registry_membership)**: These modules provide the core data models for managing individual registrants, groups, and the relationships (memberships) between them. This module extends these by creating new individual records and establishing new group memberships.
*   **[OpenSPP Service Points](spp_service_points)**: Allows the submission and processing of 'Add Child/Member' change requests through designated service points.
*   **[spp_idpass](spp_idpass)**: Integrates with this module to facilitate the capture and processing of identification document details, supporting efficient data entry through ID scanning.

## Additional Functionality

The 'spp_change_request_add_children_demo' module introduces several key features to manage the addition of new group members:

### Dedicated Change Request for Adding Members

Users can initiate a specific "Add Child/Member" change request, targeting an existing group registrant. This process guides users through a structured form to capture all necessary details for the new individual and their relationship to the group. The request then proceeds through the standard OpenSPP Change Request validation and approval workflow.

### Efficient Data Capture and Validation

The module significantly improves data entry efficiency and accuracy:

*   **ID Scanning Integration**: Users can scan physical ID documents, and the system automatically parses the information (such as family name, given name, birthdate, and ID number) to pre-populate relevant fields in the form. This minimizes manual data entry and reduces transcription errors.
*   **Comprehensive Data Fields**: The form includes fields for the new member's Full Name (automatically computed), Additional Name, Date of Birth, Gender, Phone Number, and UID Number.
*   **Built-in Data Validation**: The module enforces data quality with validations such as ensuring birthdates are not in the future, phone numbers adhere to correct formats, and UID numbers are 12 digits long. Required fields like Family Name, Given Name, Birthdate, Relationship to Applicant, and Gender are also validated before submission.

### Flexible Group Membership Definition

When adding a new member, the module allows for precise definition of their role within the group:

*   **Relationship to Applicant**: Users can specify the new member's relationship to the applicant (e.g., "Father", "Mother", "Grandfather"), providing crucial context for family-based programs.
*   **Group Membership Types**: The module integrates with the system's defined group membership kinds, allowing users to categorize the new member's role (e.g., "Dependent", "Head of Household") within the group. Upon approval, the system automatically updates the target group's membership list with the new individual and their defined role.

### Secure Document Management

All supporting documents for the 'Add Child/Member' change request, including scanned ID documents, are automatically stored within a dedicated directory in OpenSPP's Document Management System (DMS). This ensures that all evidence is securely linked to the change request, facilitating auditing and future reference.

## Conclusion

The 'OpenSPP Change Request Add Children Demo' module provides a robust and user-friendly mechanism for expanding group registries, ensuring data accuracy and a transparent, auditable process within the OpenSPP platform.