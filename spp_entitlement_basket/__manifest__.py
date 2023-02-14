# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Entitlement Basket",
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
        "spp_programs",
        "product",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/create_program_wizard.xml",
        "views/stock/entitlement_basket_view.xml",
        "views/entitlement_manager_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_entitlement_basket/static/src/css/spp_entitlement_basket.css",
        ]
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
