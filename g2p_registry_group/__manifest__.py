# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.
{
    "name": "G2P Registry: Groups",
    "category": "G2P",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "Newlogic",
    "website": "https://newlogic.com/",
    "license": "LGPL-3",
    "depends": ["base", "mail", "contacts", "g2p_registry_base"],
    "data": [
        "security/ir.model.access.csv",
        "data/group_kinds.xml",
        "views/groups_view.xml",
        "views/membership_kinds_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
