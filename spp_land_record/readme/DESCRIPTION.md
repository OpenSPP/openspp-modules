# OpenSPP Land Record

The OpenSPP Land Record module digitizes and manages land information, providing a centralized system for tracking land parcels, their associated farms, ownership details, and geospatial boundaries. This module is essential for programs requiring accurate land data to support farmer registries, agricultural initiatives, and land governance efforts.

## Purpose

This module enables comprehensive management of land-related data within OpenSPP, serving several key purposes:

*   **Centralize Land Parcel Information**: It creates a single source of truth for all land parcels, recording crucial details like parcel names, identification numbers, and acreage. This streamlines data management and reduces discrepancies.
*   **Link Land to Farms and Individuals**: The module directly connects specific land parcels to registered farms, as well as their respective owners and lessees. This linkage is critical for understanding land tenure and agricultural operations.
*   **Geospatial Visualization**: It captures and displays the geographical boundaries of land parcels and specific coordinates on interactive maps. This capability allows for visual analysis of land distribution and program coverage.
*   **Track Land Use and Tenure**: Users can classify land by its current use (e.g., cultivation, livestock, fallow) and manage lease agreements, including start and end dates. This supports informed decision-making for agricultural planning and resource allocation.
*   **Support Land Governance and Program Planning**: By providing a clear and accessible view of land assets and their attributes, the module assists in policy development, program targeting, and monitoring land-related interventions.

## Dependencies and Integration

The OpenSPP Land Record module integrates closely with other core OpenSPP components to provide its functionality:

*   **Base (base)**: As a foundational module, `base` provides the essential framework for data models, user interfaces, and core business logic within OpenSPP.
*   **OpenSPP Base GIS (spp_base_gis)**: This module is crucial for the geospatial capabilities of Land Record. It provides the underlying infrastructure for storing geographical coordinates and polygons, and for displaying these land features on interactive maps. Land Record leverages Base GIS to visualize land parcels, enabling users to view boundaries and locations directly within the system.
*   **G2P Registry Base (g2p_registry_base)**: The Land Record module relies on `g2p_registry_base` for managing the entities associated with land. It uses the `res.partner` model (extended by the registry) to link land parcels to specific farms, owners, and lessees, ensuring consistent data across the platform for individuals and groups.

## Additional Functionality

### Land Parcel Details Management

Users can meticulously record and manage individual land parcels. Each parcel can be assigned a unique **Parcel Name/ID** and its **Acreage** can be specified. The module also supports categorizing land by its **Land Use**, offering options such as "Cultivation," "Livestock," "Aquaculture," "Mixed Use," "Fallow," "Leased Out," or "Other," which helps in understanding land utilization patterns.

### Geospatial Data Capture and Mapping

A core feature is the ability to capture and visualize the geographical aspects of land. Users can define the precise **Land Polygons** that outline a parcel's boundaries and mark specific **Land Coordinates** (points) within or near the parcel. These geospatial data points are then displayed on interactive maps, providing a visual representation of land holdings and their spatial relationships. This functionality is powered by the integration with the `spp_base_gis` module.

### Ownership and Lease Tracking

The module facilitates clear tracking of who is associated with each land parcel. It allows linking a parcel to a specific **Farm** and identifying the **Owner** and, if applicable, the **Lessee**. For leased land, users can record the **Lease Start** and **Lease End** dates, providing a complete picture of land tenure and agreements. This ensures that land rights and responsibilities are clearly documented.

### Data Export for Geospatial Analysis

The module supports generating GeoJSON data for land records. This allows for the export of geospatial information in a standard format, which can then be used in external GIS applications for advanced analysis, reporting, or integration with other mapping platforms.

## Conclusion

The OpenSPP Land Record module is vital for OpenSPP, providing robust capabilities to digitize, manage, and visualize land data, thereby supporting effective land governance and program implementation.