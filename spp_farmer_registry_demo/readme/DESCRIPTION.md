# OpenSPP Farmer Registry Demo

The OpenSPP Farmer Registry Demo module provides pre-populated, realistic sample data for the OpenSPP Farmer Registry. This module is essential for showcasing the full capabilities of the Farmer Registry and enabling users to explore its features with a rich, representative dataset without manual data entry.

## Purpose

This module enables users to quickly understand and interact with the OpenSPP Farmer Registry by simulating real-world scenarios. It offers several key benefits:

*   **Accelerated System Exploration**: Users can rapidly navigate and explore the Farmer Registry's various features, forms, and reports using a comprehensive set of sample records.
*   **Realistic Data Representation**: It populates the system with diverse farmer profiles, farm details, and agricultural activities that mirror actual program data, offering a practical learning experience.
*   **Facilitated Training and Onboarding**: New users and program staff can quickly become familiar with the system's interface and data structures, reducing the learning curve and improving adoption.
*   **Robust Testing Environment**: Provides a consistent and varied dataset for testing new functionalities, customizations, or integrations within the OpenSPP ecosystem.
*   **Comprehensive Feature Showcase**: Demonstrates the depth of information the Farmer Registry can manage, from farmer demographics and land records to detailed agricultural practices and financial engagements.

## Dependencies and Integration

The `spp_farmer_registry_demo` module builds upon several core OpenSPP modules to populate their data models with sample information. It seamlessly integrates with these foundational components:

*   **[G2P Registry Base](g2p_registry_base)**: This module populates the fundamental registrant data, including individual farmer profiles and group information, leveraging the core registry structure.
*   **[OpenSPP Farmer Registry Base](spp_farmer_registry_base)**: It generates sample data for the specialized farmer, farm, land, and activity models defined in this foundational module, ensuring a complete demo of farmer-specific functionalities.
*   **[OpenSPP Farmer Registry Default Ui](spp_farmer_registry_default_ui)**: The demo data becomes visible and interactive through the user interfaces provided by this module, allowing users to experience the system as intended.
*   **[OpenSPP Base Demo](spp_base_demo)**: It extends the general demo data framework, ensuring consistency with other demo datasets across OpenSPP.
*   **Queue Job**: This technical dependency enables the efficient, asynchronous generation of large volumes of sample data, preventing system slowdowns during the demo data creation process.
*   **[OpenSPP Custom Filter Farmer Registry](spp_custom_filter_farmer_registry)**: The generated demo data can be effectively filtered and searched using the enhanced capabilities provided by this module, showcasing advanced data retrieval.

## Additional Functionality

The `spp_farmer_registry_demo` module focuses on generating a rich variety of sample data across key aspects of the Farmer Registry:

### Bulk Data Generation Interface

The module introduces a dedicated interface, accessible via the `spp.generate.farmer.data` model, allowing users to specify the number of farmer groups they wish to generate. Users can also select a specific locale (e.g., "en_KE" for Kenya) to ensure that generated names and location data are geographically relevant. This feature enables the creation of large, customized demo datasets on demand.

### Comprehensive Farmer Profiles

The demo data includes realistic individual farmer profiles, extending the base registrant information with specific details. Users can observe how the system manages diverse data points such as marital status (e.g., "Married Monogamous", "Married Polygamous"), highest education level (e.g., "Primary", "University"), household size, and contact information.

### Detailed Farm and Land Records

Sample farms are created with associated land records, demonstrating the system's ability to capture intricate farm details. This includes information like lease terms in years, agreement numbers, and whether a farmer operates multiple farms. Land records are populated with geographic coordinates and polygon shapes, showcasing the integration with GIS capabilities for visualizing farm boundaries.

### Agricultural Activity Simulation

The module generates a variety of agricultural activities per farm, including crop cultivation, livestock rearing, and aquaculture. This showcases the tracking of:
*   **Crop Rearing**: Water sources (e.g., "Irrigated", "Rainfed"), production systems (e.g., "Mono-cropping", "Agroforestry"), and chemical/fertilizer interventions.
*   **Livestock Rearing**: Production systems (e.g., "Ranching", "Zero Grazing") and feed items used.
*   **Aquaculture**: Water body types (e.g., "Freshwater", "Marine"), production systems (e.g., "Ponds", "Recirculating Systems"), and the number of fingerlings.

### Farm Assets and Technology Adoption

The demo data illustrates how the system records various farm assets and technology use. This includes machinery types, asset quantities, and their operational status. Furthermore, it showcases the tracking of farm structures (e.g., "Spray Race", "Green House"), power sources (e.g., "Solar", "Motorized"), labor sources, and equipment ownership.

### Financials and Services Engagement

Sample data is generated to demonstrate how the system captures financial information and engagement with support services. This includes a farmer's main income source (e.g., "Sale of farming produce", "Non-farm trading"), the percentage of income from farming, and participation in various groups (e.g., "Producer Group", "Table Banking Group"). It also simulates access to financial services (e.g., "Commercial Bank", "Micro-finance institutions") and information/extension services (e.g., "Radio", "Face-to-face").

## Conclusion

The `spp_farmer_registry_demo` module is a vital tool for experiencing the OpenSPP Farmer Registry, providing a rich, pre-populated dataset that enables effective exploration, training, and testing of the platform's comprehensive capabilities.