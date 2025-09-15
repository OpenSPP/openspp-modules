# OpenSPP Audit Log

The OpenSPP Audit Log module provides comprehensive tracking of all data changes and user actions across the OpenSPP platform. It ensures transparency and accountability by recording who did what, when, and what precisely changed within critical social protection programs and farmer registries.

## Purpose

The OpenSPP Audit Log module accomplishes the following key objectives:

*   **Track Data Modifications:** Records every change made to configured data, including both old and new values, to understand the evolution of critical program information over time.
*   **Monitor User Actions:** Logs specific user activities such as creating new records, updating existing ones, and deleting data, establishing a clear trail of responsibility.
*   **Enhance Accountability:** Provides an undeniable record of changes, crucial for internal audits, resolving data discrepancies, and maintaining operational integrity. For instance, it records which user modified a beneficiary's eligibility status or payment details.
*   **Support Data Integrity:** By maintaining an immutable history of changes, the module helps verify data accuracy and detect unauthorized alterations, safeguarding the reliability of OpenSPP data.
*   **Facilitate Compliance:** Assists programs in meeting regulatory and internal policy requirements for data change logging in sensitive social protection and farmer registry systems.

## Dependencies and Integration

The Audit Log module integrates with and extends core OpenSPP functionalities:

*   **Base (base):** This module leverages the fundamental data models, user management, and system architecture provided by the `base` module to capture and store audit information effectively.
*   **Mail (mail):** While not directly involved in the core logging mechanism, the `mail` module often supports general system communication and activity tracking within OpenSPP, which the audit log can complement or report on.
*   **G2P Registry Membership ([g2p_registry_membership](g2p_registry_membership)):** This dependency, along with the extension of the `res.partner` model (used for groups), demonstrates how the Audit Log module can monitor changes within complex data structures. For example, if a group's membership changes, the audit log can record the impact on computed fields like 'Group Member Names'.

The Audit Log module serves as a foundational service, enabling any other OpenSPP module to configure its data models and fields for auditing. This provides a centralized and consistent mechanism for tracking changes across all critical data, such as beneficiary profiles, program enrollments, or geographic areas.

## Additional Functionality

The OpenSPP Audit Log module offers robust features to manage and review data changes:

### Configurable Audit Rules

Users define precise rules to control what data is audited across the system. This includes selecting any OpenSPP data model (e.g., Beneficiary, Program, Location) and specifying whether to log record creation, updates, or deletions. Administrators can further refine rules by choosing to track changes to specific fields within a model, focusing only on the most critical data elements and avoiding unnecessary log entries. The system also prevents creating duplicate audit rules for the same data model.

### Detailed and Immutable Log Entries

Each log entry captures comprehensive details about the change. This includes the specific user who performed the action, the exact date and time, the record affected, and the type of operation (create, update, or delete). For updates, the log clearly displays both the old and new values of any changed fields in an easy-to-read HTML format. Crucially, audit logs are designed to be permanent and cannot be deleted by standard user actions, ensuring a tamper-proof historical record of all modifications.

### Integrated Log Viewing

The module provides convenient access to audit information directly from the records being audited. A "View logs" action menu automatically appears on audited records, allowing users to quickly access their complete historical change log. This enables program managers or auditors to immediately review the full history of changes for a specific beneficiary, program, or any other audited data point.

### Group Member Name Tracking Example

As an illustrative example of its integration capabilities, the module includes functionality to track computed fields, such as the 'Group Member Names' on the `res.partner` model (often used for managing groups). If configured for auditing, any changes to the underlying group memberships that cause this computed field to update would be logged. This provides a comprehensive view of how group compositions evolve over time, directly within the audit trail.

## Conclusion

The OpenSPP Audit Log module is an indispensable tool for ensuring data integrity, transparency, and accountability across all social protection programs and farmer registries managed within the platform.