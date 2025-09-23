# OpenSPP Entitlement Basket

The OpenSPP Entitlement Basket module empowers program administrators to define and manage structured baskets of goods and services that beneficiaries are entitled to receive. This simplifies the often complex process of distributing in-kind benefits within social protection programs, ensuring efficient and transparent delivery.

## Purpose

The OpenSPP Entitlement Basket module provides a robust framework for managing non-cash benefits, specifically designed to streamline the distribution of tangible goods. It accomplishes this by enabling users to:

*   **Define Standardized Benefit Packages**: Create predefined baskets containing specific products and quantities, such as a "monthly food basket" or a "hygiene kit." This standardizes entitlements across beneficiaries and program cycles.
*   **Automate Entitlement Calculation**: Automatically determine the precise quantity of items a beneficiary is entitled to receive, potentially based on factors like family size or specific needs.
*   **Integrate with Inventory Management**: Link in-kind entitlements directly to existing stock and warehouse operations, facilitating procurement planning and tracking the physical distribution of goods.
*   **Manage the Entitlement Lifecycle**: Support the full process from preparing draft entitlements to validating, approving, and ultimately canceling them, ensuring a controlled and auditable workflow.
*   **Enable Role-Based Validation**: Assign specific user groups the responsibility for validating entitlements, enhancing accountability and program integrity.

This module ensures that in-kind distributions, vital for many social protection initiatives, are managed with the same rigor and efficiency as cash transfers, improving program impact and reducing operational overhead.

## Dependencies and Integration

The OpenSPP Entitlement Basket module integrates seamlessly with several other OpenSPP and core Odoo modules to deliver its comprehensive functionality:

*   **[G2P Registry: Base](g2p_registry_base)**: This module relies on the foundational registrant data managed by G2P Registry: Base to identify and link entitlements to specific beneficiaries.
*   **[G2P Programs](g2p_programs)**: It extends the core program management capabilities of G2P Programs, allowing in-kind entitlements to be defined and managed as a type of benefit within program cycles.
*   **[OpenSPP Programs](spp_programs)**: Building upon OpenSPP Programs, this module introduces the specific mechanisms for handling in-kind entitlements, complementing existing cash-based distribution features.
*   **[OpenSPP Service Points](spp_service_points)**: Entitlements can be linked to specific service points where beneficiaries will collect their goods, leveraging the service point network defined in OpenSPP Service Points for distribution.
*   **Product (product)**: The module utilizes Odoo's core Product module to define and manage the individual items (e.g., rice, soap, seeds) that constitute an entitlement basket.
*   **Stock (stock)**: For programs managing physical goods, this module integrates with Odoo's Stock module to track inventory levels, manage warehouse assignments, and potentially trigger stock movements when entitlements are approved.

## Additional Functionality

### Defining Entitlement Baskets

Users can create and configure specific entitlement baskets, detailing the exact products and their quantities. Each basket serves as a template for a set of in-kind benefits. For example, a "Standard Food Basket" might include 10kg of rice, 2kg of beans, and 1 liter of cooking oil. This standardization ensures consistency across beneficiaries and simplifies program design.

### Dynamic Entitlement Calculation

The module supports dynamic calculation of entitlement quantities. Administrators can define a 'multiplier field' based on beneficiary attributes (e.g., number of household members, number of children) to automatically adjust the basket's quantity for each beneficiary. A 'maximum number' can also be set, with '0' indicating no upper limit, allowing for flexible scaling of benefits while preventing excessive distribution.

### Inventory and Distribution Management

For programs that manage physical goods, the module offers robust inventory integration. Users can specify a 'Warehouse' for each entitlement basket manager. When entitlements are approved, the system can be configured to 'manage inventory', which links directly to the Stock module to track item allocation and ensure availability at designated distribution points.

### Entitlement Lifecycle Management

The module provides a comprehensive workflow for managing in-kind entitlements through various stages:

*   **Preparation**: Generate draft entitlements for eligible beneficiaries within a program cycle.
*   **Pending Validation**: Move prepared entitlements to a pending validation state, awaiting review.
*   **Validation and Approval**: Review and approve entitlements, with the option to link to a specific 'Entitlement Validation Group' for role-based approval. Approved entitlements can trigger stock allocations.
*   **Cancellation**: Cancel entitlements that are no longer valid or required, providing flexibility in program administration.

This structured process ensures accountability and control over the distribution of in-kind benefits.

## Conclusion

The OpenSPP Entitlement Basket module is a critical component for OpenSPP, enabling the efficient and transparent management of in-kind benefits within social protection and farmer registry programs. It streamlines the definition, calculation, and distribution of goods and services, ultimately enhancing program delivery and impact.