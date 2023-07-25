# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "User Roles Management",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_group",
        "spp_area",
        "spp_idqueue",
        "base_user_role",
        "dms",
    ],
    "data": [
        "data/local_roles.xml",
        "data/global_roles.xml",
        "data/ir_cron.xml",
        "views/role.xml",
        "views/user.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
