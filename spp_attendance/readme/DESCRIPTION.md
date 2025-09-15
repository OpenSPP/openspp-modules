
# Attendance

The OpenSPP Attendance module (spp_attendance) provides a comprehensive system for managing and tracking participant attendance across various social protection programs and farmer registries. It enables organizations to accurately record who attended specific events, when, where, and for what purpose, ensuring accountability and informing program delivery.

## Purpose

This module streamlines the process of tracking participant engagement and presence, critical for program effectiveness and compliance. It accomplishes the following key capabilities:

*   **Record Participant Attendance:** Accurately logs the presence or absence of individuals at specific program events, such as training sessions, benefit distributions, or community meetings. This ensures precise data for monitoring and evaluation.
*   **Manage Program Participants:** Creates and maintains a registry of individuals participating in social protection programs, linking their attendance records to their core profile information. This centralizes participant data for easier management.
*   **Categorize Attendance Events:** Defines and categorizes different types of attendance (e.g., "Cash Transfer Distribution," "Health Education Workshop") and specific locations where these events occur. This provides granular insights into program activities.
*   **Integrate with External Systems:** Facilitates the secure import of participant data from external registries and allows external applications to submit or query attendance records via a robust API. This supports data synchronization across the OpenSPP ecosystem.
*   **Monitor Participant Engagement:** Provides tools to view an individual's attendance history and aggregated attendance data, offering valuable insights into participation patterns and program reach. This helps in assessing program impact and identifying areas for improvement.

## Dependencies and Integration

The spp_attendance module integrates seamlessly with other core OpenSPP components and extends foundational Odoo functionalities:

*   **Base (base):** As a core module, `spp_attendance` relies on the standard Odoo `base` module for fundamental system functionalities, data models, and user interface elements.
*   **OpenSPP API: Oauth (spp_oauth):** `spp_attendance` leverages the `spp_oauth` module to provide secure API access for external applications. This ensures that any attendance data submitted or queried by external systems is authenticated and authorized, protecting sensitive participant information.
*   **Partner Management (res.partner):** The module extends Odoo's core `res.partner` model to manage program participants (subscribers). Each attendance subscriber is linked to a `res.partner` record, allowing `spp_attendance` to utilize existing contact information while adding specific details relevant to program participation, such as a unique person identifier and attendance history.

This module serves as a foundational component for other program-specific modules that require accurate participant attendance records for their operations, such as benefit disbursement, case management, or training program management.

## Additional Functionality

The `spp_attendance` module offers a range of features designed to provide flexible and robust attendance management:

### Participant (Subscriber) Management

Users can create and manage detailed profiles for program participants, known as subscribers. Each subscriber is uniquely identified and linked to a core OpenSPP contact, ensuring consistency. The module automatically manages the underlying contact record when a subscriber is created or updated, including details like full name, additional names, gender, email, and phone numbers.

### Flexible Attendance Recording

The module enables recording of attendance events with specific details. For each record, users specify the attendance date, time, and category (either "Present" or "Absent"). Additional context can be added through a description and an external URL, useful for linking to external resources or evidence of attendance.

*   **Configurable Uniqueness:** System administrators can configure rules to prevent duplicate attendance entries for a single participant. This includes options to ensure uniqueness based on combinations of date, time, attendance type, and location, preventing data entry errors and ensuring data integrity.
*   **Attendance History:** Users can quickly retrieve a comprehensive attendance history for any participant, filtering by date ranges, attendance type, or location, providing a clear overview of their engagement.

### Custom Attendance Types and Locations

To accommodate diverse program needs, the module allows for the definition of custom attendance types and locations.

*   **Attendance Types:** Organizations can define various types of attendance events (e.g., "Training Session," "Cash Distribution," "Health Screening"). Each type can have a name and description, allowing for clear classification of activities.
*   **Attendance Locations:** Users can establish a list of specific locations where attendance events occur (e.g., "District Office A," "Community Hall B"). This helps in geographic tracking and reporting of program activities.

### External System Integration

The `spp_attendance` module supports integration with external systems for both data import and API-driven attendance management.

*   **Secure API Access:** Organizations can generate unique Client ID and Client Secret credentials for external applications. These credentials enable secure, authenticated access to the `spp_attendance` API, allowing external systems (e.g., mobile attendance capture apps) to submit new attendance records or query existing ones.
*   **Registry Data Import:** A dedicated wizard facilitates the import of participant data from external registries. This feature includes configurable mapping of fields (such as personal information, identifiers, and contact details) to ensure accurate and efficient synchronization of participant records into OpenSPP.

## Conclusion

The OpenSPP Attendance module is essential for effectively managing and monitoring participant engagement within social protection programs, providing robust tools for recording, categorizing, and integrating attendance data across the OpenSPP platform.