# OpenSPP Basic Cash Entitlement Spent

The OpenSPP Basic Cash Entitlement Spent module provides essential functionality for tracking how beneficiaries utilize the cash allocated to them within social protection programs. It records expenditures, calculates remaining balances, and supports ongoing program monitoring.

## Purpose

This module is designed to bring greater transparency and accountability to cash transfer programs by meticulously tracking beneficiary spending. It empowers program managers with the tools to:

*   **Monitor Cash Utilization**: Track the exact amount of cash a beneficiary has spent against their allocated entitlement.
*   **Calculate Real-time Balances**: Automatically determine the remaining balance of an entitlement after accounting for expenditures.
*   **Enhance Program Oversight**: Provide critical data for monitoring the progress and impact of basic cash programs.
*   **Ensure Financial Accountability**: Verify that disbursed funds are being utilized as intended by beneficiaries.
*   **Inform Program Adjustments**: Offer insights into spending patterns that can help refine future program design and delivery.

## Dependencies and Integration

The `spp_basic_cash_entitlement_spent` module integrates seamlessly with core OpenSPP components to extend their functionality for cash-based programs.

*   **Base (base)**: As a fundamental Odoo module, `base` provides the core technical framework, including user management, security, and basic data types, which are essential for any OpenSPP module to operate.
*   **G2P Registry Base (g2p_registry_base)**: This module relies on the foundational registrant data provided by `g2p_registry_base` to identify the beneficiaries to whom entitlements are allocated and tracked. It ensures that spending records are correctly linked to specific individuals or households.
*   **G2P Programs (g2p_programs)**: Crucially, this module extends the `g2p.entitlement` model defined within `g2p_programs`. It adds the specific fields and logic necessary to track cash spending against the entitlements established by the programs module.

## Additional Functionality

This module introduces key capabilities to manage the spending aspect of cash entitlements effectively.

### Tracking Entitlement Expenditure

Users can record the precise amount of cash a beneficiary has spent from their allocated entitlement. This feature enables program administrators to maintain an accurate and up-to-date record of funds utilization, moving beyond just disbursement to actual expenditure tracking.

### Automated Balance Calculation

The module automatically calculates the remaining balance for each entitlement. By subtracting the recorded `spent_amount` from the `initial_amount` of the entitlement, it provides an immediate and accurate view of available funds, essential for beneficiaries and program managers alike.

### Enhanced Program Monitoring

By integrating spending data with entitlement information, the module significantly enhances program monitoring capabilities. Program managers gain insights into the rate at which beneficiaries are utilizing their cash benefits, helping to identify trends, potential issues, and areas for support. This data is vital for assessing program effectiveness and beneficiary needs.

## Conclusion

The OpenSPP Basic Cash Entitlement Spent module is vital for ensuring financial accountability and enabling effective, real-time monitoring of cash transfers within OpenSPP's social protection programs.