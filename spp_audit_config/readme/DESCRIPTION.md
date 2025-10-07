# OpenSPP Audit Config

The OpenSPP Audit Config module empowers administrators to define and manage comprehensive audit rules. These rules dictate how and what data changes are tracked and logged across the OpenSPP platform, ensuring critical data remains secure, accurate, and fully auditable.

## Purpose

This module provides the essential tools for establishing a robust data governance framework within OpenSPP. It specifically aims to:

*   **Define Auditing Scope**: Administrators precisely select which data models and specific fields require audit tracking, ensuring focus on critical information.
*   **Track Data Operations**: Configure rules to log record creation, updates to chosen fields, or the deletion of records, providing a complete history of data lifecycle events.
*   **Ensure Data Integrity**: By meticulously logging changes, the module helps verify data accuracy and identify unauthorized modifications, bolstering system reliability.
*   **Support Accountability**: Every logged change includes details about the user and timestamp, establishing clear accountability for all data modifications.
*   **Enable Cross-Record Auditing**: Establish parent-child audit relationships, allowing changes in related records to be posted to their respective parent records for a consolidated view.

## Dependencies and Integration

The OpenSPP Audit Config module is foundational, integrating closely with OpenSPP's core auditing capabilities and extending its reach across various domain-specific modules:

-   **[OpenSPP Audit Log](spp_audit_log)**: This module is a direct extension of the OpenSPP Audit Log module. It provides the administrative interface and logic for defining the `spp.audit.rule` records that the Audit Log module then uses to perform the actual logging of data changes.
-   **[OpenSPP Audit Post](spp_audit_post)**: Audit Config facilitates the setup of parent-child audit relationships, a core feature provided by the Audit Post module. This allows changes in child records to be automatically recorded on associated parent records, providing a cascaded view of data modifications.
-   **[G2P Registry Membership](g2p_registry_membership)**, **[OpenSPP Programs](spp_programs)**, **[OpenSPP Service Points](spp_service_points)**: This module enables the auditing of data within these and other OpenSPP modules. For instance, administrators can define rules to track changes to program details, service point information, or membership records, ensuring oversight of key operational data.

## Additional Functionality

The OpenSPP Audit Config module offers several key features to provide flexible and powerful audit management:

### Granular Audit Rule Definition

Administrators can create and manage detailed audit rules for any data model within OpenSPP. This includes selecting specific fields to monitor for changes, such as a registrant's name or a program's status. This level of control ensures that only relevant data changes are logged, avoiding unnecessary overhead.

### Comprehensive Operation Tracking

The module allows for precise control over which types of data operations trigger an audit log entry. Users can configure rules to log when a new record is created, when an existing record is updated, or when a record is deleted. This ensures a complete historical record of how data enters, changes, and leaves the system.

### Parent-Child Audit Linking

A critical feature is the ability to establish parent-child audit relationships between different data models. For example, a rule can be set so that any change to a household member record also posts an audit message to the associated household group record. This provides a unified audit trail across interconnected data, improving traceability and context.

### Simplified Audit Log Access

For enhanced user experience, the module can automatically add a "View Logs" button to the forms of audited records. This direct link allows users to quickly access and review the complete audit history for that specific record without navigating through separate audit log menus.

## Conclusion

The OpenSPP Audit Config module is central to maintaining data integrity and accountability, providing administrators with the essential tools to flexibly define and manage comprehensive audit rules across the entire OpenSPP platform.