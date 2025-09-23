# OpenSPP Registry Approval

The OpenSPP Registry Approval module introduces a critical workflow for managing the lifecycle of registry entries, ensuring that beneficiary data meets required standards before activation. It enables a structured review and approval process for all individuals and groups within the OpenSPP system.

## Purpose

This module establishes a formal approval process for all registry entries, enhancing data quality and program integrity. It ensures that only validated and approved beneficiary data is used for program enrollment and benefit distribution.

*   **Enforce Data Quality and Compliance**: Requires review and approval of all new or updated registry entries, ensuring data accuracy and adherence to program eligibility criteria before beneficiaries can participate.
*   **Structured Workflow for Beneficiary Data**: Provides clear states (Draft, Approved, Rejected) for each registry entry, guiding users through a systematic process from data submission to final acceptance.
*   **Controlled Access to Approval Actions**: Restricts the ability to approve or reject registry entries to authorized personnel only, maintaining data integrity and accountability within the system.
*   **Prevent Premature Program Enrollment**: Ensures that beneficiaries are not inadvertently enrolled in programs or receive benefits until their registry data has been formally reviewed and approved.

## Dependencies and Integration

The OpenSPP Registry Approval module extends the core functionality of the registry by integrating directly with the base registry module.

*   **[Registry: Base](spp_registry_base)**: This module is built upon the `spp_registry_base` module, which provides the foundational framework for managing all individuals and groups within OpenSPP. The `spp_registry_approval` module enhances these core registry entries by adding the crucial approval state and associated workflow actions directly to them. This ensures that every registrant in the system can undergo a formal review process.

## Additional Functionality

### Managing Registry Entry States

The module introduces a 'State' field to each registry entry, which clearly indicates its current status in the approval workflow.
*   **Draft**: This is the initial state for any new or modified registry entry, indicating it is pending review.
*   **Approved**: Entries in this state have been formally reviewed and accepted, making them eligible for program enrollment or other operations.
*   **Rejected**: Entries in this state have been reviewed and deemed unsuitable or incorrect, preventing their use in programs until corrected and resubmitted.

### Approval Workflow Actions

Users with appropriate permissions can transition registry entries between these states, controlling their progression through the approval process.
*   **Approve Registry**: Authorized users can move a registry entry from 'Draft' to 'Approved' once it meets all necessary criteria. This action signifies that the data is verified and ready for use.
*   **Reject Registry**: If an entry contains errors or does not meet program requirements, authorized users can change its state from 'Draft' to 'Rejected'. This flags the entry as invalid and prevents its use.
*   **Reset to Draft**: For entries that were rejected or need further modifications after approval, authorized users can reset them back to the 'Draft' state. This allows for necessary corrections and re-submission for review.

### Role-Based Access Control

All approval workflow actions are secured by role-based permissions. Only users explicitly granted the 'Approve Registry', 'Reject Registry', or 'Reset Registry to Draft' roles can perform these critical operations, ensuring a controlled and secure approval process.

## Conclusion

The OpenSPP Registry Approval module is essential for maintaining high data quality and integrity within OpenSPP, providing a robust, controlled process for validating all beneficiary registry entries.