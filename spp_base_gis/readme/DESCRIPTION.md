# OpenSPP Base Gis

The `spp_base_gis` module provides foundational Geographical Information System (GIS) capabilities to the OpenSPP platform. It enables the visualization, management, and interaction with geospatial data, which is essential for geographically-aware program management and decision-making.

## Purpose

This module equips OpenSPP with robust geographical information capabilities, allowing programs to operate with a strong spatial context.

*   **Manages Geospatial Data:** It stores and organizes various types of geographical data, such as points (e.g., household locations), lines (e.g., road networks), and polygons (e.g., administrative boundaries like country > province > district). This is crucial for effectively structuring and understanding program areas.
*   **Visualizes Data on Maps:** The module displays program-related information on interactive maps, enabling users to visually analyze beneficiaries, service points, or program coverage areas. This enhances situational awareness and supports informed decision-making.
*   **Enables Spatial Querying:** Users can perform location-based queries, such as identifying all beneficiaries within a specific administrative boundary or locating service points within a certain radius. This capability is vital for targeted interventions and efficient resource allocation.
*   **Customizes Map Views:** It allows for the configuration of diverse background map layers (e.g., OpenStreetMap, satellite imagery) and the overlaying of custom program data layers. This ensures maps are tailored to specific program needs and provide relevant contextual information.
*   **Integrates Location Awareness:** By providing core GIS functionality, the module integrates with other OpenSPP modules like Registries and Targeting & Eligibility, enabling location-aware data entry, reporting, and beneficiary selection. This makes program operations more efficient and effective on the ground.

## Dependencies and Integration

The `spp_base_gis` module is a core component that integrates deeply with other parts of the OpenSPP system.

It relies on the `base` module for fundamental framework services and extends core data models like `ir.ui.view` and `ir.model.fields` to incorporate GIS-specific attributes. The `web` module is essential for rendering the interactive map interface and controls within the OpenSPP web client. Additionally, it leverages the `contacts` module to link geographical information directly to individual or organizational contact records, enhancing data completeness.

This module serves as a foundational layer, providing essential geospatial services across OpenSPP. It empowers modules such as [OpenSPP Registries](spp_registries) by allowing beneficiaries or households to be registered with precise geographical coordinates or associated with specific administrative areas. Similarly, [OpenSPP Targeting & Eligibility](spp_targeting_eligibility) utilizes these GIS capabilities to define program eligibility based on location or to target interventions to specific geographic zones, ensuring programs reach their intended recipients.

## Additional Functionality

The `spp_base_gis` module offers a range of features to manage and interact with geographical data within OpenSPP.

### Map Layer Management

Users can define and manage different types of map layers to provide comprehensive geographical context for program operations.

*   **Background Raster Layers:** Configure various base maps, including OpenStreetMap, satellite imagery, or custom Web Map Service (WMS) layers. Users can select default styles (e.g., "streets," "satellite"), adjust layer opacity, and control their initial visibility to customize the map's appearance for different use cases.
*   **Operational Data Layers:** Overlay specific program data, such as individual beneficiary locations (points), service delivery routes (lines), or administrative zones (polygons). Each data layer can be assigned a unique color, opacity, and display priority, ensuring clear visualization of all relevant program information.

### Geospatial Data Definition

The module extends OpenSPP's core data models to natively support geospatial data types, enabling precise location tracking.

Users can define specific fields within any OpenSPP record to store geographical information directly. This includes specifying the exact type of geometry (point, line, or polygon) and the spatial reference system identifier (SRID) for accurate mapping. This ensures that geographical data is consistently and accurately captured and maintained for every relevant record.

### Advanced Spatial Querying

Users can perform powerful location-based queries to analyze and retrieve data based on complex spatial relationships.

The system supports various spatial relations, such as finding records that intersect a specific area, are entirely contained within a polygon, or are within a defined distance from a given point. For instance, users can identify all households within 5 km of a health center or determine which beneficiaries reside within a specific district. This capability is crucial for targeted outreach, impact assessment, and logistical planning.

### Customizable Map Views

OpenSPP allows administrators to configure default map settings for specific views within the system, enhancing user experience.

This includes setting a default map center and initial zoom level for any GIS-enabled view, ensuring that users always see the most relevant geographic area upon opening a map. These customizable settings improve usability by providing a consistent and focused map experience tailored to specific program needs.

## Conclusion

The `spp_base_gis` module provides essential geospatial capabilities, enabling OpenSPP to manage, visualize, and analyze location-based program data, thereby enhancing the effectiveness and reach of social protection initiatives.