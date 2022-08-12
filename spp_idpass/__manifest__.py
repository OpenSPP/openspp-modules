# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "ID PASS",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "Newlogic",
    "website": "https://newlogic.com/",
    "license": "LGPL-3",
    "depends": ["base", "g2p_registry_base"],
    "data": [
        "data/id_pass.xml",
        "views/registrant.xml",
        "security/ir.model.access.csv",
        "views/id_pass_view.xml",
        "wizard/issue_id_pass_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
