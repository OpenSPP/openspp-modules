# OpenSPP Change Request

The OpenSPP Change Request module streamlines the process of modifying registrant information within the OpenSPP system. It provides a structured and auditable framework for submitting, reviewing, approving, and applying modifications to sensitive data.

## Purpose

This module enables efficient and secure management of changes to registrant data, ensuring data accuracy and accountability. It accomplishes this by:

*   **Establishing a Formal Request Process**: Users can initiate structured requests for changes to registrant information, such as updating personal details or group affiliations.
*   **Defining Multi-Stage Validation Workflows**: It supports configurable validation sequences, ensuring that changes are reviewed and approved by the appropriate personnel or departments.
*   **Maintaining an Audit Trail**: Every action taken on a change request, including submission, validation, approval, or rejection, is recorded, providing full transparency and accountability.
*   **Integrating with Document Management**: It automatically creates dedicated folders within the Document Management System (DMS) for each request, allowing for the secure storage of supporting documents.
*   **Applying Approved Changes Systematically**: Once validated and approved, the module facilitates the systematic application of changes to the main registrant records, minimizing manual data entry and errors.

This module is crucial for maintaining the integrity of social protection program and farmer registry data, ensuring that all updates follow a defined process and are thoroughly documented.

## Dependencies and Integration

The OpenSPP Change Request module integrates seamlessly with several other OpenSPP modules to provide its comprehensive functionality:

*   **[G2P Registry Base](g2p_registry_base)**: Serves as the foundational layer, providing the core registrant data structure that change requests modify.
*   **[G2P Registry Individual](g2p_registry_individual)**: Enables the submission and processing of change requests specifically targeting individual registrant profiles, such as demographic updates.
*   **[G2P Registry Group](g2p_registry_group)**: Facilitates change requests related to group entities, allowing for modifications to group details.
*   **[G2P Registry Membership](g2p_registry_membership)**: Supports changes to the relationships between individuals and groups, such as updating membership types or durations.
*   **[OpenSPP Service Points](spp_service_points)**: Service points can be involved in the submission or validation process of change requests, often serving as the initial point of contact for registrants.
*   **[OpenSPP Area](spp_area)**: Enables change requests that involve updating a registrant's associated geographical area (e.g., moving from one district to another).
*   **[OpenSPP Registry: Scan ID Document](spp_scan_id_document)**: Integrates scanning capabilities to automatically capture and populate registrant or applicant details from physical ID documents directly into the change request form.
*   **[OpenSPP Document Management System](spp_dms)**: Crucially, this module creates a dedicated DMS folder for each change request, ensuring all supporting documents, like scanned IDs or application forms, are securely stored and easily accessible.

## Additional Functionality

The Change Request module provides a robust set of features to manage the entire lifecycle of data modifications:

### Initiating and Submitting Requests

Users can create new change requests and specify the type of modification needed. This involves identifying the primary registrant (individual or group) and, if different, the applicant submitting the request. The module dynamically adjusts visible and required fields based on the selected request type, ensuring only relevant information is collected. For efficiency, it supports scanning physical ID documents or QR codes to auto-populate applicant and registrant details, reducing manual data entry and improving accuracy.

### Structured Validation Workflow

Each change request follows a defined lifecycle with distinct statuses: `Draft`, `Pending Validation`, `Validated`, `Applied`, `Rejected`, and `Cancelled`. Requests move through these stages based on user actions and configured validation sequences. The module assigns requests to specific users or validation groups, ensuring that only authorized personnel can perform review and approval steps. Users can submit requests for validation, approve them, reject them with remarks, or cancel them if no longer needed. A request can only be deleted by its original submitter if it is still in `Draft` status.

The status transitions are designed for clarity:

.. graphviz::

   digraph {
      "draft" -> "pending";
      "draft" -> "cancelled";
      "pending" -> "validated";
      "validated" -> "validated";
      "validated" -> "applied";
      "validated" -> "rejected";
      "rejected" -> "pending";
      "rejected" -> "draft";
      "rejected" -> "cancelled";
   }

This flow ensures that changes are systematically reviewed and either incorporated or formally declined.

### Integrated Document Management

Every change request automatically generates a dedicated folder within the [OpenSPP Document Management System (DMS)](spp_dms). This folder serves as a central repository for all supporting documents related to the request, such as scanned identification documents, consent forms, or other evidentiary materials. This integration ensures that all documentation is securely linked to the specific change request, providing a complete and auditable record.

### Auditability and Tracking

The module meticulously tracks the history of each change request. It records who submitted, validated, applied, rejected, or cancelled a request, along with the corresponding dates and times. In cases of rejection, specific remarks are captured, providing context and transparency. This comprehensive audit trail is vital for compliance, dispute resolution, and overall system accountability. Users can also reassign requests to different users for processing, with safeguards to ensure proper authorization.

## Conclusion

The OpenSPP Change Request module is essential for maintaining accurate, auditable, and efficiently managed registrant data within OpenSPP, providing a critical framework for all data modification processes.