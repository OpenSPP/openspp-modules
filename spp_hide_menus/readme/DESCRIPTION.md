# OpenSPP Hide Menus

The OpenSPP Hide Menus module streamlines the OpenSPP user interface by automatically hiding specific menus not directly related to core social protection program management or farmer registries. This ensures users encounter a cleaner, more focused environment tailored for their primary responsibilities.

## Purpose

This module optimizes the OpenSPP user experience by removing visual clutter and directing attention to essential program functionalities. It simplifies navigation and enhances operational efficiency for users.

*   **Streamline User Interface:** Presents a focused OpenSPP experience by hiding general-purpose modules, ensuring users see only what is relevant to their social protection program work.
*   **Reduce Menu Clutter:** Automatically removes menus such as Calendar, Contacts, Accounting, Event, Stock, and UTM from the main navigation, preventing distractions and improving clarity.
*   **Enhance User Focus:** Guides users directly to program-specific functionalities, allowing them to quickly access tools for beneficiary management, payment processing, or farmer data.
*   **Optimize Workflow:** Ensures that field agents, program managers, and data entry specialists can efficiently navigate the platform without sifting through irrelevant options.

## Dependencies and Integration

The `spp_hide_menus` module integrates with the core OpenSPP framework to manage interface elements, building upon the capabilities of its base module.

*   This module depends on the foundational [Hide Non-OpenSPP Menus: Base](spp_hide_menus_base) module, which provides the underlying mechanism for controlling menu visibility. `spp_hide_menus` leverages this base functionality to apply specific hiding configurations.
*   It interacts with standard Odoo modules like `Calendar`, `Contacts`, `Account`, `Event`, `Stock`, and `UTM` by setting their main menu items to be hidden by default. This ensures that a typical OpenSPP deployment starts with a user interface optimized for social protection programs.
*   While `spp_hide_menus` itself does not provide services to other modules, it sets a default, cleaner interface that benefits all users interacting with other OpenSPP modules by reducing cognitive load and simplifying navigation.

## Additional Functionality

### Default OpenSPP Interface Optimization

This module comes pre-configured to hide several common Odoo modules that are often not central to social protection program operations. By default, menus for **Calendar**, **Contacts**, **Accounting**, **Events**, **Stock**, and **UTM (marketing tools)** are hidden. This configuration ensures that users immediately experience an interface focused on beneficiary management, program enrollment, and other core OpenSPP functions, reducing the need for manual setup.

### Administrator Control and Flexibility

While `spp_hide_menus` applies a default set of hidden menus, administrators retain full control over their visibility. Leveraging the capabilities of the [Hide Non-OpenSPP Menus: Base](spp_hide_menus_base) module, administrators can easily unhide any of these menus if they become necessary for specific program requirements or user roles. This flexibility allows organizations to tailor the interface precisely to their operational needs.

## Conclusion

The OpenSPP Hide Menus module plays a crucial role in delivering a focused and efficient user experience by pre-configuring the visibility of non-core menus, thereby streamlining navigation for all OpenSPP users.