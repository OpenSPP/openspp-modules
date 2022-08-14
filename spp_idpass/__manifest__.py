# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "ID PASS",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp-project/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Beta",
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
