# OpenSPP Entitlement Cash

The OpenSPP Entitlement Cash module provides the essential framework for managing cash-based benefits within social protection programs. It enables administrators to define detailed calculation rules, automate the disbursement process, and meticulously track all financial payments to beneficiaries.

## Purpose

The OpenSPP Entitlement Cash module streamlines the delivery of cash benefits, ensuring efficiency, transparency, and accountability in social protection programs. It accomplishes this by:

*   **Defining Flexible Cash Entitlement Rules**: Establishes dynamic rules for calculating cash amounts, allowing for variations based on beneficiary characteristics and program criteria. For example, a program might define a base amount with additional funds for each child, up to a specified maximum.
*   **Automating Entitlement Calculation**: Automatically computes the precise cash amount each eligible beneficiary should receive based on the configured rules, reducing manual effort and errors.
*   **Managing Payment Validation Workflows**: Implements a structured process for reviewing and approving calculated entitlements, ensuring proper oversight before funds are disbursed.
*   **Facilitating Secure Fund Disbursement**: Integrates with financial systems to generate payment records and manage the transfer of funds, including accounting for any associated service fees.
*   **Ensuring Financial Control**: Incorporates checks for fund availability to prevent over-disbursement and maintains a clear audit trail of all cash transactions.

## Dependencies and Integration

The OpenSPP Entitlement Cash module integrates seamlessly with other core OpenSPP components and Odoo modules to provide its comprehensive functionality:

*   **[G2P Registry: Base](g2p_registry_base)**: This module relies on the foundational registrant data provided by `g2p_registry_base`. It uses beneficiary information, such as demographics or household composition, to apply conditions and calculate entitlement amounts based on defined multipliers.
*   **[G2P Programs](g2p_programs)**: OpenSPP Entitlement Cash extends the core program and entitlement management framework of `g2p_programs`. It specializes the general entitlement manager to specifically handle the unique requirements of cash-based benefits, building upon the common processes for program cycles and eligibility.
*   **[OpenSPP Programs](spp_programs)**: This module works in conjunction with `spp_programs` to offer a complete suite of entitlement management options. While `spp_programs` may introduce in-kind entitlements, `spp_entitlement_cash` provides the dedicated functionality for cash transfers, ensuring both types of benefits can be managed within the same platform.
*   **Account (account)**: Crucially, this module integrates with Odoo's standard accounting functionality. It generates `account.payment` records for approved entitlements, ensuring that all cash disbursements and service fees are properly recorded in the financial ledger.

## Additional Functionality

The OpenSPP Entitlement Cash module offers several key features to manage cash disbursements effectively:

### Dynamic Entitlement Rule Configuration

Users can define sophisticated rules for calculating cash entitlements. This includes specifying a base **Amount per cycle** and applying a **Condition Domain** (e.g., `[('is_woman_headed_household, '=', True)]`) to target specific beneficiary groups. Additionally, a **Multiplier** field can be selected from beneficiary data (e.g., number of children) to scale the entitlement, with an optional **Maximum number** to cap the multiplier. An overall **Maximum Amount** can also be set for any individual entitlement, overriding calculated sums if exceeded.

### Automated Entitlement Processing

Once rules are defined, the module automatically processes and generates individual cash entitlements for eligible beneficiaries within a program cycle. It evaluates each beneficiary against the specified conditions and multipliers to determine their initial entitlement amount. The system then creates draft entitlement records, ready for review and further action.

### Workflow for Validation and Approval

The module provides a structured workflow for moving entitlements from a draft state through validation to final approval. Designated user groups, specified in the **Entitlement Validation Group**, can review pending entitlements. During approval, the system automatically checks the program's fund balance to ensure sufficient funds are available before generating the necessary financial transactions in the accounting module. This process includes the creation of separate payment entries for the main disbursement and any incurred service fees.

### Entitlement Tracking and Cancellation

Administrators can monitor the status of all cash entitlements within a program cycle, viewing them as draft, pending validation, approved, or cancelled. The module also supports the cancellation of entitlements that are no longer valid or required, updating their status and ensuring an accurate record of all benefit allocations.

## Conclusion

The OpenSPP Entitlement Cash module is a vital component of OpenSPP, providing robust and flexible capabilities for the precise and auditable delivery of cash-based social protection benefits to beneficiaries.