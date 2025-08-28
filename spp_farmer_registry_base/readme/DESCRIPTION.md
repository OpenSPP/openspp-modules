# OpenSPP Farmer Registry Base

The OpenSPP Farmer Registry Base module is the core component for managing comprehensive farmer registries within OpenSPP. It provides the essential framework for recording farmer profiles, detailing farm operations, linking farms to land records, and tracking agricultural activities.

## Purpose

This module establishes the foundational system for organizing and maintaining detailed information about farmers and their agricultural endeavors. It enables users to:

*   **Manage Comprehensive Farmer Profiles**: Register and maintain detailed profiles for individual farmers, including personal demographics, contact information, and agricultural experience.
*   **Register and Detail Farm Operations**: Create and manage records for various farm types (e.g., crop, livestock, aquaculture), detailing their size, legal status, and specific agricultural practices.
*   **Link Farmers to Land and Geographic Data**: Associate farmers and farms with specific land parcels, including their geographic coordinates, and integrate with GIS for spatial visualization.
*   **Track Agricultural Activities and Seasons**: Record and monitor diverse agricultural activities, such as crop cultivation or livestock rearing, and organize them within defined agricultural seasons.
*   **Oversee Farm Assets and Extension Services**: Document farm assets, machinery, and the provision of extension services like training and advisory support.

## Dependencies and Integration

The `spp_farmer_registry_base` module integrates seamlessly with several other OpenSPP components and Odoo modules to deliver its comprehensive functionality:

*   **[G2P Registry Base](g2p_registry_base)**: Provides the fundamental registrant management capabilities, including the core `res.partner` model, which this module extends for farmers and farms.
*   **[G2P Registry Individual](g2p_registry_individual)**: Leverages individual registrant data to build detailed farmer profiles, ensuring consistency in personal information management.
*   **[G2P Registry Group](g2p_registry_group)**: Utilizes group management features, enabling the system to represent farms as groups and manage their head members.
*   **[G2P Registry Membership](g2p_registry_membership)**: Manages the critical link between individual farmers and the farms they are associated with, defining roles like "Head Member" for group farms.
*   **[OpenSPP Base GIS](spp_base_gis)**: Integrates geospatial capabilities, allowing farms and land records to be assigned GPS coordinates and visualized on maps. This enables spatial analysis and location-based program targeting.
*   **[OpenSPP Land Record](spp_land_record)**: Extends the detailed management of land parcels, including land use, species cultivated, and cultivation methods, directly linking them to farms.
*   **[OpenSPP Hide Menus](spp_hide_menus)**: Works in conjunction to ensure a streamlined user interface, focusing on farmer registry-specific functionalities by hiding less relevant Odoo menus.
*   **Base Import (base_import)**: Enhances the data import process, adding specific validations to ensure accurate and complete farmer and farm data during bulk uploads.

## Additional Functionality

### Farmer Profile Management

This module extends the core `res.partner` model to capture detailed information specific to farmers. Users can record a farmer's national identification number, years of agricultural experience, formal agricultural training, household size, and highest educational level. For group farms, the system automatically creates or updates the individual profile of the designated head farmer based on the farm's details.

### Farm Registration and Characteristics

Users can register various farm types, including crop, livestock, aquaculture, or mixed farms. The system allows for comprehensive detailing of farm size, categorizing acreage by total, under crops, under livestock, leased out, or idle. Additionally, it enables the recording of a farm's legal status, such as "owned by self," "leased," or "owned by cooperative," providing essential context for land tenure and program eligibility.

### Agricultural Activities and Seasons

The module provides tools to define and manage agricultural seasons with specific start and end dates. Within these seasons, users can record various agricultural activities, classifying them as crop cultivation, livestock rearing, or aquaculture. Activities are linked to specific species (e.g., maize, cattle, tilapia) and land parcels, ensuring a clear overview of what is being produced, where, and when. The system includes validation to prevent modifications in closed seasons and ensures only managers can activate or close seasons.

### Farm Assets, Machinery, and Extension Services

Users can track physical assets and machinery present on farms, specifying their type (e.g., tractor, irrigation pump) and working status. The module also facilitates the recording of extension services provided to farms, detailing the type of service (training, advisory), the provider, date, and topic covered. This helps monitor support provided to farmers and assess resource availability.

### Geospatial Data Integration

Each farm can be assigned precise GPS coordinates, enabling its visualization on a map via integration with the [OpenSPP Base GIS](spp_base_gis) module. This allows for the generation of GeoJSON data, supporting spatial analysis and mapping of farm locations. Land records associated with farms also include fields for cultivated species and methods (e.g., irrigated, rainfed), enriching the geospatial context.

## Conclusion

The `spp_farmer_registry_base` module is the essential foundation for managing all farmer and farm-related data within OpenSPP, providing comprehensive tools for registration, activity tracking, and geospatial integration to support effective social protection and agricultural programs.