# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Programs",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-program",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_programs",
        "spp_area",
        "product",
        "stock",
        "web_domain_field",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/main_view.xml",
        "views/entitlement_view.xml",
        "views/cycle_view.xml",
        "views/programs_view.xml",
        "views/registrant_view.xml",
        "views/inkind_entitlement_report_view.xml",
        "views/managers/eligibility_manager_view.xml",
        "wizard/inkind_entitlement_report_wiz.xml",
        "wizard/create_program_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_programs/static/src/js/hide_button.js",
        ],
    },
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
