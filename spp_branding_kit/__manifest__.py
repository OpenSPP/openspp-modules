{
    "name": "OpenSPP Branding Kit",
    "version": "17.0.1.0.0",
    "summary": "Branding customization and telemetry management for OpenSPP",
    "description": """
        OpenSPP Branding Kit
        ====================

        This module provides comprehensive branding customization for OpenSPP:

        Features:
        - Customizes system branding across all interfaces
        - Redirects telemetry to OpenSPP servers (configurable)
        - Option to completely disable telemetry
        - Removes enterprise promotion elements
        - Customizes system messages with OpenSPP branding

        Technical Features:
        - Works with theme_openspp_muk for visual styling
        - Configurable telemetry endpoint
        - Privacy-focused with opt-out options
    """,
    "author": "OpenSPP Project",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "category": "Theme/Backend",
    "depends": [
        "base",
        "web",
        "base_setup",
        "theme_openspp_muk",  # Required for OpenSPP styling
    ],
    "data": [
        # Default configuration data (order matters)
        "data/res_company_data.xml",
        "data/ir_config_parameter.xml",
        "data/debranding_data.xml",
        # Views - UI customizations
        "views/webclient_templates.xml",
        "views/login_templates.xml",
        "views/report_templates.xml",
        "views/backend_customization.xml",
        "views/res_config_settings_views.xml",
        "views/about_settings.xml",
        "views/ir_module_module_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_branding_kit/static/src/js/webclient.js",
            "spp_branding_kit/static/src/js/user_menu.js",
        ],
        "web.assets_frontend": [
            "spp_branding_kit/static/src/css/login_branding.css",
        ],
    },
    "images": [
        "static/description/icon.png",
        "static/description/banner.png",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
