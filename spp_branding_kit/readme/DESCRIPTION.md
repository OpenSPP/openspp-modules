
# OpenSPP Branding Kit

The OpenSPP Branding Kit module enables administrators to fully customize the visual identity of their OpenSPP instance and manage its telemetry settings. This module ensures that the platform consistently reflects an organization's brand and provides granular control over data sharing practices.

## Purpose

The OpenSPP Branding Kit module accomplishes several key objectives to present a unified and controlled platform experience:

*   **Customizes System Branding**: It allows organizations to replace default branding elements across all interfaces with their own, ensuring a consistent and professional appearance for users. This includes custom system names, logos, and support information.
*   **Manages Telemetry Data**: The module provides explicit control over the collection and redirection of anonymous usage statistics, allowing organizations to comply with privacy policies or disable telemetry entirely. This supports data sovereignty requirements.
*   **Removes Non-OpenSPP Elements**: It removes or replaces references to other platforms and promotional content, presenting a clean, OpenSPP-centric user experience. This helps avoid confusion and maintains focus on the social protection program.
*   **Standardizes System Messages**: It customizes default system messages and email signatures to align with OpenSPP branding and communication standards. This reinforces the platform's identity in all user interactions.
*   **Optimizes User Interface**: The module streamlines the user interface for OpenSPP-specific workflows, enhancing usability and relevance for social protection program managers and field staff.

## Dependencies and Integration

The OpenSPP Branding Kit is a foundational module that integrates deeply with the OpenSPP core and other thematic modules to provide a consistent user experience.

*   It depends on the `base`, `web`, and `base_setup` modules for core system functionality, web client operations, and basic configuration settings, respectively.
*   Crucially, it relies on the :ref:`theme_openspp_muk` module to apply the visual styling and layout that defines the OpenSPP aesthetic. The Branding Kit then layers specific customizations on top of this theme.
*   This module serves other OpenSPP modules by establishing a standardized visual and operational environment. By setting system-wide branding and telemetry rules, it ensures that all other modules operate within a consistent, OpenSPP-branded framework.

## Additional Functionality

The module offers comprehensive features for brand management and operational control within the OpenSPP platform.

### Customizing System Information and Visuals

Administrators can personalize various aspects of the OpenSPP interface to match their organization's identity. This includes setting a custom system name, defining specific documentation and support URLs, and controlling the visibility of "Powered by OpenSPP" branding. These changes are reflected across the entire platform, including the login page, system reports, and the backend user interface, ensuring a cohesive look and feel. The module also overrides default email signatures to incorporate OpenSPP branding automatically.

### Telemetry and Data Privacy Control

The Branding Kit provides essential tools for managing data privacy. Organizations can easily enable or disable the collection of anonymous usage statistics (telemetry) directly from the system settings. For active telemetry, administrators can configure a custom endpoint where this data is sent, allowing for compliance with specific data governance policies or redirection to internal analytics services. This feature empowers organizations to control their data footprint effectively.

### Interface Optimization

To provide a focused OpenSPP experience, this module removes or modifies elements that refer to other platforms or promote non-OpenSPP services. This includes removing external account URLs from user profiles and optimizing the interface to highlight OpenSPP-specific workflows. By streamlining the user experience and eliminating extraneous content, the module ensures that the platform remains dedicated to its primary mission of social protection program management.

## Conclusion

The OpenSPP Branding Kit is a pivotal module that empowers organizations to fully brand their OpenSPP instance and manage telemetry, delivering a professional, consistent, and privacy-compliant platform for social protection programs.