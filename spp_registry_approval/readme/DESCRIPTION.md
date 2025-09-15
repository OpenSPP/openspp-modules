
# Registry Approval: Base

The OpenSPP Registry Approval module establishes a crucial workflow for validating and managing the official status of individuals and groups within the OpenSPP registry. It ensures that all registrant data is formally reviewed and approved before being utilized in social protection programs or farmer registries.

## Purpose

This module provides a structured approval process for registrant data, ensuring its accuracy, compliance, and readiness for program participation. It acts as a gatekeeper, maintaining the integrity of the OpenSPP registry.

*   **Formal Approval Workflow**: Establishes a structured process for reviewing and validating registrant data, moving it through defined stages. This ensures that all entries meet established criteria before becoming active.
*   **Clear Status Tracking**: Provides a clear and consistent way to track the current status of each registrant (Draft, Approved, Rejected). This transparency allows users to understand where a registrant is in the validation lifecycle.
*   **Data Quality Assurance**: Acts as a critical checkpoint to prevent unverified or non-compliant data from being used in programs, thereby safeguarding the overall quality of the registry.
*   **Role-Based Decision Making**: Empowers authorized personnel, such as program managers or data validators, to make final decisions on the validity and eligibility of registrant entries.
*   **Streamlined Program Enrollment**: Ensures that only approved and verified individuals or groups are eligible for enrollment in social protection programs, preventing errors and ensuring proper resource allocation.

## Dependencies and Integration

The OpenSPP Registry Approval module extends the core registrant data model provided by the [OpenSPP Registry Base](spp_registry_base) module. It integrates directly by adding the essential approval `state` field to all registrant records.

This module serves as a foundational component for other program-specific modules that rely on validated beneficiary data. By providing clear approval statuses, it ensures that only officially approved individuals and groups are considered for benefits, program enrollment, or further processing across the OpenSPP platform.

## Additional Functionality

### Registrant Status Management

The module introduces a 'State' field for every registrant, allowing users to track their progress through the approval workflow. New registrants typically begin in a 'Draft' state, awaiting review. This status provides immediate insight into whether a registrant is pending, active, or disallowed.

### Approval and Rejection Actions

Authorized users can change a registrant's state based on review outcomes. The 'Approve' action transitions a registrant from 'Draft' to 'Approved', signaling that their data is verified and they are eligible for program inclusion. Conversely, the 'Reject' action marks a registrant as 'Rejected', indicating that they do not meet the criteria or their data is invalid.

### Reset to Draft for Re-evaluation

In cases where an 'Approved' or 'Rejected' registrant requires further edits or a new review cycle, authorized users can utilize the 'Reset to Draft' action. This reverts the registrant to the initial 'Draft' state, allowing for necessary modifications and a subsequent re-submission for approval.

### Role-Based Access Control

All approval, rejection, and reset actions are protected by specific user roles and permissions. This ensures that only designated personnel, such as data validators or program administrators, can modify a registrant's approval status, maintaining data integrity and accountability within the system.

## Conclusion

The `spp_registry_approval` module is vital for maintaining data integrity and compliance by providing a structured approval workflow for all individuals and groups within OpenSPP's social protection and farmer registries.