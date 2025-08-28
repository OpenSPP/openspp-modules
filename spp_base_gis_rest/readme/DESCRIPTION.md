# OpenSPP Base Gis Rest

The OpenSPP Base GIS REST module provides secure, programmatic access to OpenSPP's Geographical Information System (GIS) data through a set of RESTful API endpoints. It leverages industry-standard OAuth 2.0 for robust authentication, enabling external applications and services to integrate with and consume geospatial information from the OpenSPP platform.

## Purpose

This module empowers external systems to securely interact with OpenSPP's GIS capabilities, facilitating data exchange and integration. It achieves this by:

*   **Enabling Programmatic GIS Access:** Provides secure API endpoints, allowing external applications to query and retrieve geospatial data like administrative boundaries or beneficiary locations.
*   **Supporting Industry-Standard Authentication:** Offers robust security through OAuth 2.0 (Bearer tokens) and Basic authentication for API clients, ensuring only authorized systems access sensitive data.
*   **Managing API Client Credentials:** Allows for the creation and management of unique Client IDs, Client Secrets, and Client Tokens required for API access, ensuring controlled and traceable interactions.
*   **Facilitating External System Integration:** Bridges OpenSPP's rich GIS data with other platforms, supporting custom dashboards, analytical tools, and broader data ecosystems.
*   **Enhancing Data Interoperability:** Makes OpenSPP's geospatial data readily available for consumption by other systems, promoting seamless data flow and collaborative program management.

## Dependencies and Integration

The OpenSPP Base GIS REST module is foundational for exposing geospatial data programmatically and relies on other core OpenSPP modules to function effectively.

It primarily depends on the [OpenSPP Base GIS](spp_base_gis) module, which provides the underlying GIS data models, mapping capabilities, and spatial querying functionalities. This module acts as the API layer, making the rich geospatial information managed by `spp_base_gis` accessible to external systems.

For secure access, the module integrates with the [OpenSPP API: Oauth](spp_oauth) module. `spp_oauth` provides the robust OAuth 2.0 authentication framework, ensuring that all API requests to the GIS endpoints are properly authenticated and authorized before data is exposed. This synergy ensures both functionality and security for GIS data access.

## Additional Functionality

### API Client Credential Management

The module enables administrators to create and manage credentials for various external applications that require access to OpenSPP's GIS APIs. Each client can be configured with a unique name and assigned specific authentication details. It supports both Bearer token (OAuth 2.0) and Basic authentication methods, generating unique Client IDs, Client Secrets, or Client Tokens as required.

### Secure Credential Viewing

For enhanced security, sensitive API client credentials, such as the Client ID and Client Secret, are displayed only once upon their initial creation. This design choice prevents accidental exposure and encourages best practices for handling confidential access keys. If credentials are lost or compromised, administrators must generate new ones to maintain security.

### Programmatic GIS Data Access

This module provides the necessary RESTful API endpoints that allow authorized external systems to programmatically query and retrieve geospatial data. This includes accessing administrative boundaries (e.g., country > province > district), locations of program sites, or spatial data associated with beneficiaries. This capability is crucial for integrating OpenSPP's GIS information into custom dashboards, analytical platforms, or other applications that require real-time geospatial insights.

### Access Token Generation

The module includes functionality to generate time-limited access tokens for authenticated API clients. These tokens, typically valid for a short duration (e.g., 10 minutes), provide temporary authorization for API requests. This mechanism enhances security by limiting the window of opportunity for token misuse and requires clients to periodically refresh their access.

## Conclusion

The OpenSPP Base GIS REST module is critical for extending OpenSPP's geospatial capabilities, securely exposing GIS data via RESTful APIs for integration with external applications and services. It ensures that valuable geographic insights from social protection programs are accessible and actionable across a broader digital ecosystem.