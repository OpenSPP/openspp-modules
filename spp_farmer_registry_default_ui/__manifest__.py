# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Farmer Registry Default UI",
    "summary": "This module delivers the essential user interface components for managing OpenSPP farmer and farm registry data. It enables streamlined farmer registration, efficient farm management, and accessible entry of agricultural activity and asset information.",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["reichie020212"],
    "depends": [
        "spp_farmer_registry_base",
    ],
    "excludes": [
        "spp_base",
    ],
    "data": [
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
