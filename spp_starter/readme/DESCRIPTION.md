# OpenSPP Starter

The `spp_starter` module provides a guided, step-by-step setup wizard designed to configure a new OpenSPP instance. It simplifies the initial deployment process by helping users define their core program needs and automatically installing the necessary OpenSPP modules.

## Purpose

The OpenSPP Starter module streamlines the initial configuration of your OpenSPP system, ensuring it is tailored to your specific program requirements from the outset.

*   **Guided System Setup**: It walks new users through a multi-step process to define the fundamental aspects of their social protection program. This reduces complexity and ensures all critical initial configurations are addressed.
*   **Program Type Specialization**: Users can select between a Social Protection Management Information System (SP-MIS) or a Farmer Registry, which then customizes the subsequent setup steps and module installations. This ensures the system is purpose-built for the chosen program.
*   **Automated Module Installation**: Based on user choices for features like location management, identity verification, or transfer types, the module automatically installs the relevant OpenSPP components. This eliminates manual module selection and ensures a complete, functional system.
*   **Core Company Information Review**: It facilitates the review and adjustment of essential organizational details such as company name, address, phone number, and default currency. This ensures accurate record-keeping and financial setup from day one.
*   **Initial Data Cleanup**: After the setup is complete, the module automatically removes any default demo products and hides the setup wizard menu, providing a clean and production-ready environment. This helps maintain data integrity and a focused user interface.

## Dependencies and Integration

The OpenSPP Starter module relies on core system components to function and acts as a foundational installer for other OpenSPP modules.

It depends on the `base` module, which provides the fundamental Odoo framework and core functionalities, and the `product` module, essential for managing goods and services, particularly relevant for in-kind transfer programs.

This module is foundational as it dynamically provisions and installs other OpenSPP modules based on user selections during the setup wizard. It intelligently integrates with the system's configuration parameters and menu management (`ir.ui.menu`) to control its own visibility and to guide users through the initial setup, effectively serving as the gateway to a tailored OpenSPP ecosystem.

## Additional Functionality

The OpenSPP Starter module offers several key features to ensure a smooth and customized initial deployment of your OpenSPP instance.

### Guided Setup Workflow

The module presents a logical, multi-step wizard that guides users through essential configuration decisions. This structured approach covers organizational details, the selection of your primary registry type, and specific feature requirements, ensuring no critical step is missed during initial setup.

### Program Type Specialization

A core capability is the ability to choose between an **SP-MIS (Social Protection Management Information System)** or a **Farmer Registry** as the primary focus of your OpenSPP deployment. This crucial decision tailors the subsequent configuration options and the set of modules automatically installed, ensuring the system aligns perfectly with your program's objectives.

### Dynamic Module Provisioning

Based on your selections within the wizard, the module intelligently determines and installs the necessary OpenSPP components. This includes modules for:
*   **Location Assignment**: To manage geographical hierarchies (e.g., country > province > district).
*   **Identity Management**: For robust beneficiary identification and verification.
*   **Service Point Management**: For tracking and managing service delivery locations.
*   **Cash Transfer Functionality**: To enable and manage financial disbursements.
*   **In-Kind Transfer Functionality**: To support the distribution and tracking of goods.
*   **Demo Data Management**: To optionally install example data for initial testing and learning.

This automated installation process simplifies system deployment and reduces the effort required to configure a fully functional OpenSPP instance.

### System Initialization and Cleanup

The module assists in reviewing and, if necessary, adjusting your organization's core details, such as its name, address, phone, and default currency. Upon completion of the setup, it performs essential cleanup by removing default demo products and hiding the Starter module's menu entry. This ensures your OpenSPP environment is clean, focused, and ready for production use.

## Conclusion

The OpenSPP Starter module is an indispensable tool that provides a clear, guided pathway for initial system setup, ensuring OpenSPP instances are precisely configured and ready to support specific social protection or farmer registry programs from day one.