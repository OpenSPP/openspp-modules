# OpenSPP API

The OpenSPP API module provides a robust framework for building and managing a RESTful API (Application Programming Interface) for the OpenSPP platform. It enables external systems and applications to securely interact with OpenSPP data and functionalities, facilitating seamless integration, data exchange, and automation.

## Purpose

This module serves as the central hub for OpenSPP's external communication, offering a structured way to expose and manage platform capabilities. It accomplishes the following key objectives:

*   **Standardized Data Access:** Establishes a consistent and secure method for external applications to read, create, update, and delete OpenSPP data, such as beneficiary records or program details.
*   **Customizable API Endpoints:** Allows users to define specific API endpoints for various OpenSPP data models and operations, tailoring the API to the exact needs of integrated systems.
*   **Enhanced Security:** Implements authentication and authorization mechanisms to ensure that only authorized users and systems can access and manipulate sensitive program information.
*   **Comprehensive Logging and Auditing:** Provides detailed logging of all API interactions, offering transparency, aiding in troubleshooting, and supporting compliance requirements.
*   **Flexible Data Mapping:** Enables the renaming and configuration of data fields exposed through the API, making integration simpler and more intuitive for external systems.

## Dependencies and Integration

The `spp_api` module is foundational to OpenSPP's external connectivity, building upon other core modules to deliver its capabilities:

*   It leverages the [OpenSPP Base API](spp_base_api) module, which provides essential, low-level API functions and methods for interacting with OpenSPP models. This ensures a consistent foundation for all API operations.
*   Security for API access is handled by the [OpenSPP API: Oauth](spp_oauth) module, which implements secure authentication protocols and token management. This module ensures that all API requests are properly authorized before accessing OpenSPP resources.
*   The module integrates with the core `mail` module, likely for sending notifications or alerts related to API activities or issues.
*   It utilizes the `web` module for exposing API endpoints over the web, making them accessible to external applications.

Together, these integrations allow `spp_api` to provide a secure, functional, and extensible API layer for the entire OpenSPP platform.

## Additional Functionality

The `spp_api` module offers a range of features to configure and manage API interactions effectively.

### API Namespace and Endpoint Configuration

Users can define distinct API namespaces to group related endpoints, manage versions, and control access. Each namespace acts as a unique integration point, such as 'Beneficiary_Service_v1' or 'Financial_Aid_v2'. Within these namespaces, specific API paths (endpoints) are created for individual OpenSPP data models (e.g., "Beneficiary", "Program"). For each path, users configure:

*   **Supported Operations:** Define whether external systems can read (GET), create (POST), update (PUT), delete (DELETE), or perform custom (PATCH) actions on the data.
*   **Data Filtering and Limits:** For read operations, specify default filters (e.g., only active beneficiaries) and set limits on the number of records returned.
*   **Custom Functions:** Implement custom business logic as API endpoints, complete with defined input parameters.

### Data Field Customization

To simplify integration, the module allows granular control over how data fields appear in the API:

*   **Field Selection:** For read operations, specify exactly which fields of an OpenSPP model are exposed, preventing unnecessary data transfer.
*   **Required Fields and Default Values:** For create and update operations, mark specific fields as mandatory or provide default values, ensuring data consistency.
*   **Field Aliases:** Rename internal OpenSPP field names to more intuitive, external-facing names within the API. For instance, an internal field like `b_dob` (beneficiary date of birth) can be aliased to `beneficiary_birthdate` for clarity in the API. These aliases can be global or specific to an API path.

### API Security and Logging

The module provides essential tools for securing and monitoring API usage:

*   **User API Tokens:** OpenSPP users can generate unique API tokens to authenticate their external applications. These tokens are essential for secure access to the API.
*   **Namespace-based Access Control:** Assign specific API namespaces to individual OpenSPP users, granting them access only to the integrations they need.
*   **Detailed API Logs:** All API requests and responses are logged, including method, model, and the data exchanged. This provides a comprehensive audit trail, crucial for debugging, security monitoring, and compliance. Users can configure logging levels (disabled, short, full) for both requests and responses.

### Advanced API Operations

Beyond standard CRUD (Create, Read, Update, Delete) operations, the module supports custom API functions:

*   **Custom Function Parameters:** Define specific parameters (e.g., name, type, required status, default value) for custom API functions, allowing external systems to trigger complex business processes within OpenSPP.
*   **Record-Specific Actions:** Custom functions can be configured to apply either globally or on specific records, offering flexibility for targeted actions.

## Conclusion

The `spp_api` module is indispensable for extending OpenSPP's reach, enabling secure, flexible, and auditable integration with external systems to streamline social protection program management and data exchange.