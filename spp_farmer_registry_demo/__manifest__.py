# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Farmer Registry: Demo",
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
        "spp_farmer_registry_base",
    ],
    "data": [
        "data/aqua_data.xml",
        "data/crop_data.xml",
        "data/livestock_data.xml",
        "views/group_view.xml",
        "views/individual_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
