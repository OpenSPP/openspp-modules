# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Registrant Tags",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "external_dependencies": {
        "python": [
            "python-magic",
        ]
    },
    "depends": [
        "base",
        "g2p_registry_base",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "OpenSPP registrants gain enhanced tagging capabilities through this module, allowing granular categorization by specific attributes, program statuses, or needs. It extends the G2P Registry Base module, improving data findability and facilitating targeted interventions with flexible tag management.",
}
