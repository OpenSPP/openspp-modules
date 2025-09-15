# OpenSPP Event Demo

The OpenSPP Event Demo module provides practical examples and templates for tracking specific events within OpenSPP's social protection programs. It showcases how to leverage the core event management framework by offering predefined event types, data structures, and user interfaces, serving as a blueprint for custom event implementation.

## Purpose

This module demonstrates and facilitates the use of OpenSPP's event tracking system by providing concrete, ready-to-use examples. It aims to:

*   **Illustrate Event Types**: Offers predefined event categories such as House Visits, Phone Surveys, and School Enrolment Records, showing how different program interactions can be tracked.
*   **Showcase Data Models**: Provides complete data models for each demonstration event type, detailing how specific information (e.g., farm size for a house visit) can be captured and stored.
*   **Present User Interfaces**: Includes functional views and wizards for managing these event types, demonstrating streamlined data entry and record-keeping processes.
*   **Extend Registrant Profiles**: Adds capabilities to registrant profiles (res.partner) to quickly access and view the active status of specific event types relevant to an individual.
*   **Accelerate Customization**: Serves as a practical guide for organizations to design and implement their own unique event types tailored to specific program needs.

## Dependencies and Integration

The OpenSPP Event Demo module is built upon foundational OpenSPP components, extending their capabilities to offer concrete event tracking examples.

-   **Base Module**: This module relies on the standard Odoo base module for core system functionalities.
-   **[OpenSPP Event Data](spp_event_data)**: The `spp_event_demo` module is a direct extension of the `spp_event_data` framework. It defines the specific event types (like house visits or phone surveys) that the `spp_event_data` module then manages and links to registrants. This integration provides the underlying structure for recording and associating event details with individuals.

This module primarily serves as a template for other OpenSPP modules or custom implementations that need to define and integrate their own specific event types. By observing its structure, developers and implementers can understand how to create new event models and integrate them into the broader OpenSPP event tracking system.

## Additional Functionality

The OpenSPP Event Demo module introduces several key features to demonstrate practical event management.

### Comprehensive Event Record Types

The module defines specific event types with detailed data capture capabilities:

*   **House Visit Records**: Users can record detailed information about physical house visits, including whether a property is a farm, its size in acres, and counts of livestock like pigs and cows. It also allows for photo uploads and notes on food stock or disability status, providing a rich dataset for field assessments.
*   **Phone Survey Records**: This feature enables the systematic recording of phone survey outcomes. Users can capture a concise summary of the call and a more detailed description of the conversation or findings, facilitating remote data collection and interaction tracking.
*   **School Enrolment Records**: Organizations can track educational participation by recording details of school enrolment. This includes the name of the school, the specific enrolment type, and the date of enrolment, providing insights into a registrant's educational status.

### Streamlined Event Creation Wizards

To simplify data entry and ensure consistency, the module includes dedicated wizards for creating new event records:

*   **Guided Creation**: Wizards for House Visits, Phone Surveys, and School Enrolment records guide users through the necessary steps to create a new event. This ensures all required information is captured accurately and efficiently.
*   **User-Friendly Interface**: These wizards streamline the process, making it easier for program staff to log new events without extensive training.

### Registrant Event Overview

The module enhances the registrant's profile (res.partner) to provide a quick overview of associated events:

*   **Active Event Links**: Registrant profiles display direct links to the *active* House Visit, Phone Survey, and School Enrolment records. This allows users to immediately see the latest and most relevant event data pertaining to an individual, improving data accessibility and program monitoring.

## Conclusion

The OpenSPP Event Demo module is a crucial component for understanding and extending OpenSPP's event tracking capabilities. It provides practical, ready-to-use examples of event types and their management, serving as a vital guide for organizations to implement and customize their social protection program's event logging requirements effectively.