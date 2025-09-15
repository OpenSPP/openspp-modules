
# Hide Non-OpenSPP Menus

The OpenSPP Hide Menus module streamlines the OpenSPP platform by automatically hiding standard Odoo menu items that are not typically essential for core social protection program management. This creates a focused user interface, ensuring users primarily interact with functionalities relevant to their specific roles and program objectives.

## Purpose

This module is designed to declutter the OpenSPP interface by pre-configuring the visibility of common Odoo menus. It establishes a more focused and efficient working environment, particularly beneficial for OpenSPP users involved in field operations or specialized program tasks.

*   **Streamline User Experience:** Automatically hides menus from modules like Calendar, Contacts, Accounting, and Inventory, providing a cleaner, OpenSPP-centric interface. This ensures field agents or case workers see only relevant program functions.
*   **Enhance Operational Focus:** Reduces distractions and simplifies navigation, allowing users to quickly access the tools they need for managing beneficiaries, programs, or farmer registries without sifting through unrelated options.
*   **Improve System Adoption:** A less cluttered interface is easier to learn and navigate, which helps increase user comfort and reduces the training overhead for new OpenSPP users.
*   **Tailor for Specific Deployments:** While [OpenSPP Hide Menus Base](spp_hide_menus_base) offers granular control, this module provides an immediate, default simplification, making OpenSPP more ready-to-use for typical social protection deployments.

## Dependencies and Integration

The `spp_hide_menus` module leverages the foundational capabilities of the [OpenSPP Hide Menus Base](spp_hide_menus_base) module to manage menu visibility.

*   It directly depends on [OpenSPP Hide Menus Base](spp_hide_menus_base), which provides the core mechanism for administrators to define and control menu visibility. This module builds upon that foundation by applying a specific set of predefined visibility rules.
*   This module interacts with standard Odoo modules such as Calendar, Contacts, Account, Event, Stock, and UTM. Its primary function is to hide the default menu items provided by these modules, thereby creating a more focused OpenSPP environment.
*   By pre-hiding these menus, `spp_hide_menus` ensures that users primarily interact with modules central to social protection, like beneficiary management or program enrollment, immediately upon system deployment.

## Additional Functionality

This module's core functionality is to apply a predefined set of menu visibility rules to simplify the OpenSPP interface.

### Default Menu Simplification
Upon installation, this module automatically sets common Odoo menu items to be hidden from most OpenSPP users. This includes menus typically found in areas like general accounting, inventory management, and broad contact lists, which are often not directly relevant to the daily tasks of social protection program staff. This immediate simplification helps focus users on core program activities.

### Enhanced User Focus
By default, the module configures the system so that users will primarily see menus related to OpenSPP's core functions. This ensures a streamlined experience, reducing the time users spend searching for specific features and minimizing cognitive load. For instance, a field agent will directly access beneficiary registration or case management without navigating through unrelated business modules.

### Administrator Override
While this module provides a default simplified view, administrators retain full control. They can use the underlying [OpenSPP Hide Menus Base](spp_hide_menus_base) module to unhide any of these menus if a specific deployment requires access to, for example, the Calendar or Contacts module for certain user groups. This flexibility ensures the system can adapt to evolving program needs without losing the initial benefit of a focused interface.

## Conclusion

The `spp_hide_menus` module delivers a focused and efficient OpenSPP user experience by strategically hiding non-essential standard Odoo menus, thus optimizing the platform for social protection program management.