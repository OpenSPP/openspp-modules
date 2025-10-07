
# Grievance Redress Mechanism

The OpenSPP Grm module provides a robust Grievance Redress Mechanism (GRM) for managing and resolving complaints and feedback within social protection programs and farmer registries. It offers a structured way to receive, track, and address issues raised by registrants.

## Purpose

The OpenSPP Grm module enables organizations to manage grievances effectively, fostering accountability and transparency. It ensures that feedback from beneficiaries and stakeholders is systematically captured and addressed.

Key capabilities include:

*   **Centralized Grievance Management**: Provides a single system for logging, tracking, and resolving all incoming grievances, ensuring no issue is overlooked.
*   **Multi-Channel Intake**: Supports grievance submission through various channels, including direct entry by staff, automated creation from emails, and registrant self-service via a dedicated portal.
*   **Structured Workflow**: Defines clear, customizable stages for each grievance, guiding staff through the resolution process from initial receipt to closure.
*   **Enhanced Communication**: Facilitates timely and transparent communication with registrants, including automated notifications on status changes and a dedicated portal for tracking.
*   **Performance Monitoring**: Allows for categorization, prioritization, and assignment of grievances, providing insights into common issues and team performance.

This module ensures that registrants have a clear avenue to voice concerns and receive timely responses, improving program trust and effectiveness.

## Dependencies and Integration

The spp_grm module integrates with core OpenSPP components to provide a comprehensive grievance management solution:

*   **Portal**: Enables registrants to submit new grievances and track the status of their existing tickets through a secure online portal.
*   **Mail (mail)**: Leverages Odoo's mail system to automatically create grievance tickets from incoming emails and send automated notifications to registrants when a ticket's status changes.
*   **[G2P Registry: Base](g2p_registry_base)**, **[G2P Registry: Individual](g2p_registry_individual)**, and **[G2P Registry: Group](g2p_registry_group)**: Links grievances directly to specific registrants, whether individuals or groups, ensuring all communication and history are tied to the correct profile. This provides a complete view of a registrant's interactions.
*   **[OpenSPP Area](spp_area)**: While spp_grm does not directly manage geographical areas, it works with registrants who are associated with specific areas via the spp_area module. This allows for location-aware grievance management and reporting.
*   **[OpenSPP User Roles](spp_user_roles)**: Integrates with user role management to assign grievances to appropriate staff based on their roles and potentially restrict access to tickets based on assigned areas, ensuring staff manage only relevant grievances.

## Additional Functionality

The spp_grm module offers a range of features to streamline grievance management:

### Grievance Intake and Creation
Users can create new grievance tickets manually within the system, or tickets can be automatically generated from incoming emails. Registrants can also submit grievances directly through the OpenSPP portal, which automatically creates a new ticket. Each ticket receives a unique identifier for easy tracking.

### Structured Workflow and Stages
Grievances progress through customizable stages, such as 'New', 'In Progress', 'Resolved', and 'Closed'. Each stage can trigger automated email notifications to the registrant, keeping them informed of the ticket's progress. The system also supports a Kanban view for visual workflow management, allowing stages to be folded when empty.

### Categorization, Channels, and Prioritization
Staff can categorize grievances (e.g., "Payment Issue," "Data Correction"), assign a channel through which the grievance was received (e.g., "Email," "Phone Call," "In-Person"), and apply descriptive tags. Each grievance can also be assigned a priority level (Low, Medium, High, Very High) to help manage workload and ensure urgent issues are addressed promptly.

### Registrant-Centric Tracking
Every grievance ticket is linked directly to the relevant registrant (individual or group). This allows staff to view all past and active grievances associated with a specific registrant from their profile, providing a comprehensive history of interactions.

### Communication and Attachments
The module includes an integrated messaging thread for internal and external communication related to each grievance. Email replies are automatically added to the ticket's history. Users can also attach relevant documents and media to tickets, such as photos or supporting evidence.

### Portal Access for Registrants
Registrants who have submitted grievances can log into the OpenSPP portal to view the status, history, and details of their submitted tickets. This self-service capability reduces the burden on staff and increases transparency for beneficiaries.

## Conclusion

The OpenSPP Grm module is essential for establishing an accountable and responsive social protection program by providing a comprehensive system for managing and resolving grievances efficiently.
