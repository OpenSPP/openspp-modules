# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Farmer Registry: Base",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "base_geoengine",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/kind_data.xml",
        "views/configuration_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
