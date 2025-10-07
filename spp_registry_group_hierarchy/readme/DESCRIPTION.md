# OpenSPP Registry Group Hierarchy

This module extends OpenSPP's registry capabilities by introducing hierarchical relationships among groups. It enables the creation of nested group structures, allowing groups to contain both individual members and other sub-groups, which is crucial for managing complex social protection programs and farmer registries effectively.

## Purpose

The `spp_registry_group_hierarchy` module enhances the organization and management of registrants by:

*   **Establishing Nested Group Structures:** Allows groups to be members of other groups, forming multi-level hierarchies. For example, a regional cooperative can contain several local farmer groups, or a village committee can oversee various household groups.
*   **Enabling Flexible Membership Types:** Provides the ability to define group types that can include a mix of individual registrants and other groups as members, offering greater flexibility in program design and representation.
*   **Improving Data Organization:** Organizes complex social structures or administrative units within the system, accurately reflecting real-world organizational arrangements and reporting lines.
*   **Enhancing Program Management:** Supports the management of programs that operate across multiple levels of aggregation, from individual beneficiaries up to large organizational structures.

## Dependencies and Integration

The `spp_registry_group_hierarchy` module builds upon and extends several core OpenSPP registry modules to introduce its hierarchical capabilities:

*   It extends **[G2P Registry Groups](g2p_registry_group)** by modifying the `g2p.group.kind` model. This module adds a field to specify if a particular group type can include both individual and other group members, laying the groundwork for nested structures.
*   It integrates closely with **[G2P Registry Membership](g2p_registry_membership)** by enhancing the `g2p.group.membership` model. This allows membership records to correctly link to either individual registrants or other groups, dynamically managing how members are selected and displayed within the system.
*   The module also relies on **[G2P Registry Base](g2p_registry_base)** and **[G2P Registry Individual](g2p_registry_individual)**, as these modules provide the fundamental registrant and individual data structures that form the lowest level of any hierarchy.

## Additional Functionality

The `spp_registry_group_hierarchy` module introduces key features for managing complex, multi-level group structures:

### Group Kind Configuration for Hierarchy
Administrators can configure specific types of groups to allow for hierarchical membership. When defining a group kind (e.g., "Regional Cooperative"), an option is available to permit this kind of group to contain both individual members and other sub-groups (e.g., "Local Farmer Groups"). This setting provides granular control over the structure and composition of different group types within the system.

### Dynamic Member Selection
When adding members to a group, the system intelligently adjusts the available options based on the parent group's configured "kind." If the group's kind allows for mixed membership, users can select either individual registrants or other existing groups to be members. This streamlines the process of building complex hierarchies without requiring manual workarounds.

### Seamless Navigation to Group Members
The module enhances the user experience by allowing direct navigation to the detailed view of a group member. If a member within a hierarchical group is itself another group, users can click to instantly access that sub-group's full profile and membership details, facilitating efficient management and oversight of nested structures.

## Conclusion

The OpenSPP Registry Group Hierarchy module is vital for managing intricate social protection programs and farmer registries, enabling the system to accurately model and manage nested organizational structures by allowing groups to contain both individuals and other groups as members.