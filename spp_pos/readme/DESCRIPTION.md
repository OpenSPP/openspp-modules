# OpenSPP Pos

The OpenSPP Pos module extends the standard Odoo Point of Sale (POS) system to facilitate the secure and efficient redemption of social protection entitlements. It integrates directly with OpenSPP's entitlement management system, allowing beneficiaries to redeem their benefits at participating retail locations.

## Purpose

The `spp_pos` module provides a critical link between social protection programs and beneficiaries at the point of transaction. It enables the seamless and controlled distribution of benefits through retail channels.

*   **Secure Entitlement Redemption**: Allows beneficiaries to redeem their specific entitlements (e.g., vouchers, credits) directly at a POS terminal. This ensures that benefits reach the intended recipients for authorized goods or services.
*   **Real-time Validation**: Validates entitlement codes instantly, checking their existence, amount, and status to prevent fraudulent or expired redemptions. This enhances program integrity and reduces losses.
*   **Streamlined Transaction Processing**: Integrates entitlement redemption into the standard POS workflow, simplifying the process for both beneficiaries and POS operators. This improves efficiency and reduces wait times.
*   **Controlled Product Access**: Designates specific products that can only be purchased using entitlements, ensuring that program funds are spent according to program rules. For example, a food assistance program can ensure funds are used only for approved food items.
*   **Enhanced Beneficiary Service**: Provides a quick and transparent mechanism for beneficiaries to access their benefits, improving their experience and trust in the program.

## Dependencies and Integration

The `spp_pos` module integrates with key OpenSPP and Odoo modules to provide its functionality:

*   **Point of Sale (`point_of_sale`)**: This module extends the core Odoo Point of Sale functionality, adding the necessary features for entitlement redemption. It leverages the existing POS interface and workflows.
*   **G2P Registry Base (`g2p_registry_base`)**: While not a direct dependency, `spp_pos` interacts with `g2p.entitlement` which itself relies on `g2p_registry_base` for core beneficiary and registrant data. This ensures that entitlements are linked to verified beneficiaries.
*   **G2P Programs (`g2p_programs`)**: This is a crucial dependency as `spp_pos` is designed to redeem `g2p.entitlement` records, which are generated and managed by the `g2p_programs` module. `spp_pos` provides the final step in the entitlement lifecycle by enabling their consumption.

The `spp_pos` module serves as the operational interface for the final delivery of benefits defined and managed by the `g2p_programs` module, ensuring that the entitlements created can be effectively utilized by beneficiaries.

## Additional Functionality

The `spp_pos` module introduces several key features to manage entitlement redemptions:

### Entitlement Redemption Workflow

POS operators can initiate an entitlement redemption by scanning or manually entering an entitlement code (e.g., a QR code or alphanumeric string). The system then performs a real-time lookup against the `g2p.entitlement` records, verifying the entitlement's validity and available amount. If valid, the entitlement's value is applied to the POS transaction, and the entitlement status is updated accordingly. If the entitlement is invalid or does not exist, the POS operator receives an immediate notification.

### Dedicated Entitlement Products and Categories

To clearly distinguish entitlement-based transactions from regular sales, the module introduces a specific product template and a dedicated POS category. This allows for:
*   **Clear Identification**: A designated "Entitlement Product" simplifies the POS interface for operators when processing entitlement redemptions.
*   **Organized Reporting**: Separating entitlement-related items into their own category helps in financial tracking and reporting for social protection programs.

### Product Locking for Entitlement Use

The `spp_pos` module adds an `is_locked` field to `product.template` records. This allows administrators to mark specific products as "locked," meaning they can only be purchased using a valid entitlement and cannot be bought with standard payment methods like cash or card. This feature is vital for:
*   **Program Compliance**: Ensures that program funds are used exclusively for their intended purpose, such as specific food items or educational supplies.
*   **Fraud Prevention**: Prevents the misuse or unauthorized sale of subsidized goods, maintaining the integrity of the social protection program.

## Conclusion

The OpenSPP Pos module is essential for the last-mile delivery of social protection benefits, providing a secure, efficient, and controlled mechanism for beneficiaries to redeem their entitlements at the point of sale.