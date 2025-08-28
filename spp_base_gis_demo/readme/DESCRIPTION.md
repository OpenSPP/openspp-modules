# OpenSPP Base Gis Demo

The OpenSPP Base GIS Demo module provides practical examples and use cases for integrating and leveraging the Geographical Information System (GIS) capabilities within the OpenSPP platform. It demonstrates how to add and visualize geospatial data using the foundational OpenSPP Base GIS module.

## Purpose

This module showcases how OpenSPP programs can incorporate location-based data into their operations, enabling more informed decision-making and improved program management. It provides a blueprint for implementing GIS features, helping users understand their practical application.

Key capabilities include:

*   **Illustrating Geospatial Data Integration:** Demonstrates how to extend existing OpenSPP data models with various geographical field types (points, lines, polygons). This allows for associating precise location data with beneficiaries, facilities, or program areas.
*   **Showcasing Custom GIS Models:** Provides examples of defining new data models specifically designed to store and manage complex geospatial entities within OpenSPP. This is useful for managing custom geographic layers relevant to a program.
*   **Visualizing Location-Based Information:** Offers concrete examples of how to display these diverse geographical data types on interactive maps within OpenSPP's GIS views. Users can see how points, lines, and polygons are rendered and interacted with.
*   **Accelerating GIS Implementation:** Serves as a practical guide for developers and implementers, illustrating the steps to integrate and utilize OpenSPP's GIS capabilities effectively for their specific program needs.

The module's value lies in making OpenSPP's GIS features tangible, showing how to transform abstract location data into actionable insights for program planning, monitoring, and evaluation. For instance, it can demonstrate how to plot beneficiary homes (points), define service boundaries (polygons), or map distribution routes (lines).

## Dependencies and Integration

The OpenSPP Base GIS Demo module relies on core OpenSPP functionalities to operate and extends the platform's geospatial capabilities.

It primarily depends on:

*   **base**: This dependency provides the fundamental framework and standard functionalities of OpenSPP, essential for any module.
*   **[OpenSPP Base GIS](spp_base_gis)**: This is the foundational GIS module that introduces all core geospatial data types and map visualization features. The `spp_base_gis_demo` module specifically *demonstrates* how to utilize the capabilities provided by `spp_base_gis`, acting as an implementation guide rather than adding new core GIS features itself.

This module serves as a practical extension, showing how to apply the powerful GIS tools from `spp_base_gis` to real-world OpenSPP data. It helps other modules, like those managing registries or program targeting, understand how they can integrate and display their location-sensitive data.

## Additional Functionality

The `spp_base_gis_demo` module focuses on providing clear, functional examples of how to work with geospatial data within OpenSPP.

### Extending Existing OpenSPP Models with Location Data

This module demonstrates how to easily add geographical information to standard OpenSPP records. For example, it extends the `res.partner` model, allowing users to associate specific location types with partners. This includes adding a `geo_point` for a partner's exact location, a `geo_line` to represent a route, or a `geo_polygon_field` to define a service area. Users can input and manage these geographical coordinates directly on partner records.

### Demonstrating Custom GIS Data Models

The module includes an example of a dedicated GIS data model, `spp.base.gis.test.model`, which showcases how to create new OpenSPP models specifically for geospatial data. This model incorporates various geographic field types—points, lines, and polygons—allowing implementers to see how to structure and manage complex spatial datasets within OpenSPP. This is useful for applications requiring custom map layers or spatial analysis.

### Visualizing Diverse Geospatial Data Types

Through its examples, the module illustrates how different geospatial data types are displayed and interacted with on OpenSPP's maps. It provides a visual guide for understanding how `geo_point` fields appear as markers, `geo_line` fields as paths, and `geo_polygon_field` fields as shaded areas. This helps users grasp the visual representation of their data and plan how to best present their location-based information.

## Conclusion

The OpenSPP Base GIS Demo module is a vital resource for understanding and practically applying the robust GIS capabilities available in OpenSPP. It serves as a hands-on guide for integrating and visualizing location-based data, enhancing the platform's ability to manage social protection programs with a strong spatial dimension.