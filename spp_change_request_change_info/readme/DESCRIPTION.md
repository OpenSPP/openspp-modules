
# Change Information Change Request

The OpenSPP Change Request Change Info module streamlines the process of updating and managing an individual registrant's personal and demographic information within the OpenSPP platform. It provides a structured and validated approach for making modifications to existing registrant profiles.

## Purpose

This module enables users to efficiently manage and apply changes to individual registrant data, ensuring that all information remains current and accurate. It accomplishes this by:

*   **Standardizing Individual Profile Updates**: It provides a dedicated and formal process for submitting requests to modify personal and demographic details of individual registrants.
*   **Streamlining Data Capture**: The module integrates with ID scanning technology to quickly and accurately extract and populate registrant information from official documents.
*   **Ensuring Data Accuracy and Completeness**: It enforces validation rules for critical data fields, such as birthdates and national ID numbers, to maintain high data quality.
*   **Integrating with Approval Workflows**: Changes submitted through this module follow the established OpenSPP change request and approval framework, ensuring proper authorization before application.
*   **Maintaining an Audit Trail**: Every change request and its associated modifications are documented, providing a clear history of all updates to registrant information.

## Dependencies and Integration

The `spp_change_request_change_info` module integrates closely with several other OpenSPP modules to deliver its functionality:

*   **`spp_change_request`**: This module extends the core [OpenSPP Change Request](spp_change_request) framework by adding a specialized request type specifically for modifying individual registrant information. It leverages the parent module's workflow, validation sequences, and overall management of change requests.

*   **`g2p_registry_individual`**: This module directly interacts with the [G2P Registry Individual](g2p_registry_individual) module to update the personal and demographic data of individual registrants. It modifies fields such as names, birthdate, gender, and identification details stored within an individual's profile.

*   **`g2p_registry_group`** and **`g2p_registry_membership`**: These modules are foundational components of the broader OpenSPP G2P Registry. While this specific 'Change Information' module focuses exclusively on individual registrant updates and does not directly modify group or membership data, it operates within the comprehensive registry framework that includes these modules.

*   **`spp_service_points`**: [OpenSPP Service Points](spp_service_points) agents utilize this module to initiate and process change requests for registrant information directly from their service locations, facilitating decentralized data management.

*   **Document Management System (DMS)**: The module integrates with the OpenSPP Document Management System (DMS) to store supporting documentation, such as scanned ID documents, securely alongside the change request for verification and audit purposes.

## Additional Functionality

### Comprehensive Personal Data Updates

Users can update a wide range of personal details for an individual registrant, ensuring their profile accurately reflects current information. This includes modifying their given name, family name, additional name, place of birth, date of birth, gender, and contact phone number. The module validates that the date of birth is not in the future and ensures phone numbers adhere to correct formatting standards.

### National ID and Photo Management

This module allows for the management of official identification details and the registrant's profile photograph. Users can update the national ID number, which is validated to be a 12-digit entry, and upload a new profile picture. This functionality is crucial for identity verification and maintaining up-to-date records for program eligibility.

### Streamlined Data Capture via ID Scanning

A key feature is the ability to quickly and accurately populate registrant details by processing scanned ID documents. The system automatically extracts information such as name, birthdate, gender, and place of birth from scanned documents (e.g., UID cards), pre-filling the relevant fields. The scanned image is also automatically uploaded and stored within the Document Management System, significantly reducing manual data entry errors and accelerating the change request process.

### Educational and Relationship Information

Beyond core personal details, the module supports recording and updating additional demographic and relational information. Users can specify the registrant's highest educational level attained and define their relationship to an applicant (e.g., father, mother, grandfather). This enriches registrant profiles, providing valuable data for program targeting and analysis.

## Conclusion

The OpenSPP Change Request Change Info module is essential for maintaining accurate and up-to-date individual registrant data within the OpenSPP platform, ensuring data integrity and supporting efficient program administration.