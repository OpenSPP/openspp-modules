# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.
{
    "name": "G2P Registry: Base",
    "category": "G2P",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "Newlogic",
    "website": "https://newlogic.com/",
    "license": "LGPL-3",
    "depends": ["base", "mail", "contacts", "web"],
    "data": [
        "security/g2p_security.xml",
        "security/ir.model.access.csv",
        "wizard/disable_registrant_view.xml",
        "views/main_view.xml",
        "views/reg_relationship_view.xml",
        "views/relationships_view.xml",
        "views/reg_id_view.xml",
        "views/id_types_view.xml",
        "views/phone_number_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/g2p_registry_base/static/src/js/custom_client_action.js",
        ],
        "web.assets_qweb": [
            "g2p_registry_base/static/src/xml/custom_web.xml",
        ],
    },
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
