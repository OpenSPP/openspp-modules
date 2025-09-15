
# Cycle: Attendance Compliance

The OpenSPP Cycle Attendance Compliance module integrates attendance records as a key criterion for determining beneficiary eligibility and ongoing compliance within social protection programs. It allows program managers to define, track, and enforce attendance requirements for beneficiaries participating in program cycles, ensuring accountability and program integrity.

## Purpose

This module enhances OpenSPP's ability to manage beneficiary compliance by incorporating attendance data. It achieves this by:

*   **Defining Attendance Requirements**: Enables program administrators to specify a minimum number of attendance days or sessions required for beneficiaries within a program cycle.
*   **Integrating External Attendance Data**: Connects OpenSPP with external attendance tracking systems to retrieve real-time attendance records for program participants.
*   **Automating Compliance Checks**: Automatically filters and updates beneficiary compliance status within program cycles based on their attendance records against predefined criteria.
*   **Maintaining Detailed Attendance History**: Stores a comprehensive log of individual attendance events directly within OpenSPP, providing an auditable history for each beneficiary.
*   **Supporting Group and Individual Programs**: Manages attendance compliance for both individual beneficiaries and for members within group-based programs.

This module ensures that only beneficiaries who meet the required attendance levels remain active in a program, helping to optimize resource allocation and verify active participation. For example, a program might require beneficiaries to attend a minimum of 10 health awareness sessions over a cycle to receive their next payment.

## Dependencies and Integration

The OpenSPP Cycle Attendance Compliance module seamlessly integrates with core OpenSPP functionalities and extends existing modules:

*   **[OpenSPP Programs: Compliance Criteria](spp_programs_compliance_criteria)**: This module extends the foundational compliance framework. It introduces attendance as a specific type of compliance criterion that can be applied to beneficiaries during program cycles, building upon the general compliance management features.
*   **[OpenSPP Event Data](spp_event_data)**: It leverages the event data framework to store detailed attendance records. When attendance data is fetched from an external system, individual attendance events (like a specific date and time of attendance) are logged as `spp.event.attendance` records, which are then managed by the `spp_event_data` module.
*   **G2P Cycle Management (g2p_cycle)**: It extends the program cycle model, allowing program managers to enable attendance criteria and configure specific requirements (e.g., required attendance days, date ranges) directly on the cycle.

## Additional Functionality

### External Attendance System Configuration

Program administrators can configure OpenSPP to connect with an external attendance tracking system. This involves setting up the external server URL, authentication endpoints, client credentials (ID and secret), and specific API endpoints for fetching attendance types, locations, and compliance data. A "Test Connection" feature allows administrators to verify the connection and automatically import attendance types and locations from the external system into OpenSPP's configuration. This ensures that attendance data is consistently categorized.

### Program Cycle Attendance Criteria Definition

Within each program cycle, administrators gain the ability to activate and define specific attendance compliance rules. They can:

*   Enable or disable the use of attendance criteria for the cycle.
*   Specify the **required number of attendance days** or sessions a beneficiary must complete.
*   Define a **date range (From Date, To Date)** within which attendance will be considered.
*   Optionally, select a specific **Attendance Type** (e.g., "Training Session," "Health Check-up") and **Attendance Location** (e.g., "Community Center A," "District Office") to filter records from the external system.

### Automated Beneficiary Compliance Filtering

When the "Filter Beneficiaries by Compliance Criteria" action is triggered on a program cycle, this module automatically fetches attendance data for all eligible registrants from the configured external system. It then compares each beneficiary's attendance count against the `required_number_of_attendance` set for the cycle.

*   **Individual Programs**: For programs targeting individuals, beneficiaries who meet the attendance threshold are marked as 'enrolled', while those who do not are set to 'non_compliant'. The exact `number_of_attendance` is recorded on their cycle membership.
*   **Group Programs**: For programs targeting groups, the module assesses attendance for each individual member within the group. A group's overall compliance might depend on a certain number or percentage of its members meeting the attendance criteria, and each member's attendance status (`included` or `not_included`) is tracked within the group's cycle membership.

### Detailed Attendance Event Logging

Upon fetching attendance data from the external system, the module not only updates compliance statuses but also creates detailed `spp.event.attendance` records within OpenSPP for each individual attendance event. These records capture the date, time, type, location, and source of attendance, providing a granular history for each beneficiary. This ensures that a complete, auditable trail of attendance is maintained directly within OpenSPP, accessible for review and reporting.

## Conclusion

The OpenSPP Cycle Attendance Compliance module provides essential capabilities for managing and enforcing attendance-based compliance criteria, thereby strengthening program integrity and ensuring that social protection benefits reach actively participating beneficiaries.