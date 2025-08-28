# OpenSPP Api Records

The OpenSPP Api Records module provides a robust set of RESTful API endpoints, serving as the primary interface for external systems to access and manage OpenSPP's core operational data. It enables programmatic interaction with critical information such as service points, social protection programs, product definitions, and beneficiary entitlements.

## Purpose

This module is designed to empower external applications and integrated systems to interact seamlessly with the OpenSPP platform. It achieves this by:

*   **Exposing Core Data Entities**: Provides direct, secure access to foundational OpenSPP data models like service points, programs, products, and entitlements.
*   **Enabling Data Retrieval and Management**: Allows external systems to query, create, update, and potentially delete key records, facilitating comprehensive data management.
*   **Supporting External Integrations**: Serves as the backbone for integrating OpenSPP with mobile applications, third-party reporting tools, and other digital platforms.
*   **Standardizing Data Access**: Offers a consistent and documented API interface, simplifying development and reducing integration complexity for partners.
*   **Enhancing Operational Efficiency**: Streamlines data exchange, for example, by allowing mobile agents to retrieve beneficiary entitlements or service points to update product stock information.

## Dependencies and Integration

The `spp_api_records` module builds upon the core API framework provided by [OpenSPP API](spp_api), which defines the foundational structure for creating and securing API endpoints. Its primary function is to expose data managed by various other OpenSPP modules:

*   **[OpenSPP Service Points](spp_service_points)** and **[OpenSPP Service Point Device](spp_service_point_device)**: This module exposes the comprehensive data related to service points and their associated devices, allowing external systems to query locations, operational status, and hardware information.
*   **[G2P Programs](g2p_programs)** and **[OpenSPP Programs](spp_programs)**: It provides access to the definitions and configurations of social protection programs, including program cycles and associated companies.
*   **Product (product)** and **UoM (uom)**: Enables external systems to retrieve detailed product information, including images and units of measure, for in-kind entitlement management.
*   **Entitlement Modules ([OpenSPP Cash Entitlement](spp_entitlement_cash), [OpenSPP In-Kind Entitlement](spp_entitlement_in_kind), [OpenSPP Entitlement Transactions](spp_ent_trans))**: This module makes all entitlement-related data available, covering both cash and in-kind benefits, as well as the history of entitlement transactions.
*   **Foundational Data Modules ([G2P Registry Base](g2p_registry_base), Contacts (contacts), [OpenSPP Area](spp_area), [OpenSPP Programs: Service Points Integration](spp_programs_sp))**: It exposes underlying registry data, contact information, geographical area structures, and program-service point linkages, providing complete context for the exposed records.

This module acts as a data gateway, centralizing access to diverse OpenSPP data sets through a single, consistent API.

## Additional Functionality

The `spp_api_records` module enhances and exposes key data from various OpenSPP components, enabling comprehensive external system interaction.

*   **Comprehensive Service Point Information**: The module exposes detailed service point records, including a computed list of associated programs. This allows external applications to retrieve not only service point details but also understand their active program affiliations derived from entitlements, crucial for operational planning and reporting.
*   **Program and Product Catalog Access**: External systems can access a full catalog of defined social protection programs, including the managing company. Furthermore, it exposes product details, crucially including a dynamically generated image URL for each product, enabling richer display in external applications like beneficiary portals or mobile agent tools.
*   **Detailed Entitlement and Transaction Data**: The API provides access to both cash and in-kind entitlement records, enriched with computed fields that clarify the beneficiary type (individual or group) and the entitlement's specific nature (cash or in-kind). It also exposes the `cycle_number` for entitlements, linking them directly to program cycles. This enables external systems to accurately track beneficiary benefits and their status.
*   **Standardized Unit of Measure Data**: The module exposes unit of measure (UoM) definitions, including their symbols. This ensures consistency when displaying product quantities and values in external applications, particularly for in-kind distributions.

## Conclusion

The OpenSPP Api Records module is essential for enabling OpenSPP's interoperability, providing external systems with a structured and secure way to access and manage the platform's core social protection and farmer registry data.