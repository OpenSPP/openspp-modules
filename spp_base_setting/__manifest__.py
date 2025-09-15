# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Base Settings",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "g2p_registry_base",
    ],
    "data": [
        "views/country_office_views.xml",
        "views/res_users_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "OpenSPP Base Setting provides fundamental configurations for country implementations, establishing core organizational structures such as Country Offices. It also enables tailored user interface adaptations and streamlines user management by linking individuals to specific Country Offices for context-aware data access.",
}
