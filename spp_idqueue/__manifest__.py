# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "ID Queueing Management",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp-project/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "g2p_registry_base", "spp_idpass"],
    "data": [
        "security/g2p_security.xml",
        "security/ir.model.access.csv",
        "views/id_queue_view.xml",
        "wizard/request_id_wizard.xml",
        "views/registrant.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
