# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP SMS",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "AGPL-3",
    "depends": ["iap", "sms", "mass_mailing_sms", "g2p_registry_base", "g2p_programs"],
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "external_dependencies": {
        "python": [
            "twilio",
            "boto3",
        ]
    },
    "data": [
        "data/iap_account_data.xml",
        "views/iap_account_view.xml",
        "views/mailing_mailing.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
