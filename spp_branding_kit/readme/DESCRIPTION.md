# OpenSPP Branding Kit

This document describes the **OpenSPP Branding Kit** module, which provides comprehensive debranding and rebranding functionality for Odoo 17 installations used within the OpenSPP ecosystem.

## Purpose

The **OpenSPP Branding Kit** module is designed to:

* **Apply OpenSPP Branding**: Replace removed Odoo branding with OpenSPP-specific branding elements, including logos, colors, text, and system information.
* **Control Telemetry and External Communications**: Provide administrators with control over telemetry data collection and external service communications.
* **Hide Paid Applications**: Optionally filter out enterprise and paid Odoo applications from the Apps menu to focus on open-source modules.
* **Customize System Behavior**: Offer configuration options for system naming, documentation URLs, and support links.

## Dependencies and Integration

1. **Odoo 17 Core**: This module is built specifically for Odoo 17 and utilizes its standard extension mechanisms.

2. **OpenSPP Muk Theme ([theme_openspp_muk](theme_openspp_muk))**: Depends on the OpenSPP Muk theme module which provides the base visual theme and styling framework for the OpenSPP platform.


## Additional Functionality

* **Configuration Management ([ir.config_parameter](ir.config_parameter))**:
    * Introduces system-wide configuration parameters with the `openspp.*` prefix for centralized branding control.
    * Provides settings for system name, documentation URLs, support links, and telemetry endpoints.
    * Enables toggle options for features like hiding paid apps.

* **Module Filtering ([ir.module.module](ir.module.module))**:
    * Implements intelligent filtering of paid applications (OEEL and OPL licensed modules) from the Apps menu.
    * Maintains visibility of paid modules in administrative views while hiding them from the standard Apps interface.
    * Provides helper methods for counting and filtering paid applications.

* **Web Interface Customization**:
    * Provides custom routes for OpenSPP-specific information pages.
    * Modifies session information to include OpenSPP branding data.
    * Implements telemetry redirection to OpenSPP endpoints when enabled.

* **Company Branding Updates ([res.company](res.company))**:
    * Automatically updates company information with OpenSPP branding during module installation.
    * Sets default report headers and footers with OpenSPP information.
    * Updates company website references to OpenSPP URLs.

* **User Interface Enhancements**:
    * Customizes login page styling with OpenSPP branding.
    * Modifies backend interface colors and styling.
    * Updates user menu items and removes Odoo-specific links.
    * Provides custom email signature templates.

* **Security and Privacy Features**:
    * Disables unnecessary telemetry and external communications by default.
    * Removes promotional content and enterprise upselling elements.
    * Implements proper permission controls for branding configuration.

## Module Components

* **Controllers**: Custom HTTP routes for OpenSPP-specific pages and version information.
* **Models**: Extensions to core Odoo models for branding customization.
* **Data Files**: XML configuration for default parameters and company settings.
* **Views**: XML templates for UI customization across backend, login, and report interfaces.
* **Static Assets**: CSS, JavaScript, and image files for visual branding.
* **Tests**: Comprehensive test suite ensuring proper functionality and coverage.

## Installation Hooks

* **Post-Installation Hook**: Automatically applies initial branding configuration, disables Odoo promotional elements, and updates company information.
* **Uninstall Hook**: Cleanly removes OpenSPP configuration parameters while preserving user data.

## Configuration Options

The module provides various configuration parameters that can be adjusted through the Settings interface or directly via system parameters:

* `openspp.system.name`: Custom system name displayed throughout the interface
* `openspp.telemetry.enabled`: Enable or disable telemetry data collection
* `openspp.documentation.url`: Custom documentation URL for help links
* `openspp.support.url`: Custom support URL for assistance

## Conclusion

The **OpenSPP Branding Kit** module provides a complete solution for transforming an Odoo 17 installation into a fully branded OpenSPP platform. It ensures consistent branding across all interfaces while maintaining system functionality and providing administrators with granular control over branding and behavior settings. The module's modular architecture and adherence to Odoo best practices ensure compatibility with future updates and seamless integration with other OpenSPP modules.
