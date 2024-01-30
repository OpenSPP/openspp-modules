# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Proxy Means Testing",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["dasunhegoda"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_group",
        "spp_custom_fields_ui",
        "spp_area",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/custom_fields_ui_view.xml",
        "views/custom_registrant_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
