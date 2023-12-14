# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Dashboard",
    "category": "OpenSPP",
    "version": "15.0.1.1.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "g2p_registry_base", "g2p_programs", "odoo_dynamic_dashboard"],
    "data": [
        "views/main_view.xml",
        "data/dashboard_templates.xml",
        "views/dashboard_menu_view.xml",
        "views/dashboard_block_view.xml",
        "views/programs_view.xml",
        "views/cycles_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_dashboard/static/src/js/dynamic_dashboard.js",
        ],
        "web.assets_qweb": [],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
