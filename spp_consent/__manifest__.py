# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Consent",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "Newlogic",
    "website": "https://newlogic.com/",
    "license": "LGPL-3",
    "depends": ["base", "g2p_registry_base", "g2p_registry_individual"],
    "data": [
        "security/ir.model.access.csv",
        "data/default_consent_config.xml",
        "views/registrant_view.xml",
        "views/expired_consent_view.xml",
        "wizard/create_consent.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
