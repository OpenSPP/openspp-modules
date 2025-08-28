# OpenSPP Service Points

The OpenSPP Service Points module streamlines the management of physical or virtual locations where social protection services are delivered. It links these service points to geographical areas, company entities, and user accounts, ensuring efficient and localized program implementation.

## Purpose

The OpenSPP Service Points module facilitates the organized delivery of services by:

*   **Establishing Service Point Locations**: Defines and manages all operational service points, which can be physical offices, mobile units, or virtual hubs, ensuring beneficiaries can access support.
*   **Categorizing Service Offerings**: Associates each service point with specific types of services it provides, such as registration, payments, or information dissemination, to guide beneficiaries and staff.
*   **Geographical Alignment**: Links service points to specific administrative areas (e.g., country > province > district > village), enabling targeted service delivery and localized program oversight.
*   **Organizational Integration**: Connects service points with the company entities or organizations responsible for their operation, clarifying administrative structures and accountability.
*   **User Access Management**: Assigns authorized users (agents) to specific service points, granting them the necessary access to manage and deliver services effectively.

## Dependencies and Integration

The OpenSPP Service Points module integrates seamlessly with other core OpenSPP components to provide comprehensive functionality:

*   **G2P Registry Base** (`g2p_registry_base`): This module extends the foundational registrant management capabilities by allowing service points to be associated with individuals and companies (`res.partner`). It leverages the base contact system for organizational linking.
*   **Phone Validation** (`phone_validation`): Ensures that all phone numbers recorded for service points are correctly formatted and validated according to international standards, improving communication reliability.
*   **OpenSPP Area** (`spp_area`): This module is crucial for defining the geographical context of service points. It allows service points to be linked to the hierarchical administrative areas managed by the [OpenSPP Area](spp_area) module, facilitating location-based service planning and reporting.

This module also extends the `res.users` model, allowing user accounts to be directly associated with one or more service points. This ensures that users, such as service agents, only access and manage data relevant to their assigned service delivery locations.

## Additional Functionality

The OpenSPP Service Points module provides robust features for managing service delivery operations:

### Service Point Definition and Management

Users can create and manage individual service points, defining key attributes such as the agent's name, physical address, and assigned geographical area. Each service point can be linked to a specific company entity responsible for its operations. This structured approach ensures clear accountability and an organized overview of all service delivery locations.

### Service Type Classification

The module allows for the creation and assignment of various service types (e.g., "Cash Transfer Enrollment," "Grievance Redress," "Information Desk"). Users can associate multiple service types with a single service point, clearly indicating the range of services available at each location and facilitating specialized service delivery.

### Status and Availability Control

Service points can be actively managed by enabling or disabling them as needed. This feature includes recording the date a service point was disabled and the reason, providing a clear audit trail and allowing for temporary or permanent suspension of services. This is critical for managing operational changes or temporary closures.

### User and Registrant Association

Service points are directly linked to OpenSPP users (service agents) and registrant records. This allows the system to automatically assign individuals and companies to relevant service points, ensuring that beneficiaries are directed to appropriate locations and that agents only have access to data pertinent to their operational scope. The module also supports the creation of user accounts for contacts associated with a service point's company.

```{note}
When creating users for a service point's company contacts, the system automatically assigns them to the "Service Point Users" group, ensuring appropriate access rights.
```

## Conclusion

The OpenSPP Service Points module is essential for organizing, managing, and delivering social protection services efficiently by linking service locations with geographical areas, organizations, and personnel.