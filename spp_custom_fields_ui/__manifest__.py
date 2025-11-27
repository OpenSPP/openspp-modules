{
    "name": "OpenSPP Custom Fields UI",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "g2p_registry_base", "g2p_registry_membership", "spp_custom_field"],
    "data": ["views/custom_fields_ui.xml"],
    "assets": {
        "web.assets_backend": [
            "spp_custom_fields_ui/static/src/js/custom_fields_ui_reload.js",
        ],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "The OpenSPP Custom Fields UI module provides a user interface for program implementers to define and manage custom data fields for registrants. It extends registrant profiles by associating custom data with individuals or groups, supporting program-specific indicators and calculated data points within the OpenSPP platform.",
}
