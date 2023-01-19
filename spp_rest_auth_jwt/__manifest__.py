# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP JWT Rest API Authentication",
    "category": "OpenSPP",
    "version": "15.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "emjay0921"],
    "depends": ["base_rest"],
    "external_dependencies": {
        "python": [
            "apispec",
            "pyjwt>=2.4.0",
            "pyOpenSSL==22.0.0",
        ]
    },
    "data": [
        "security/ir.model.access.csv",
        "views/auth_jwt_validator_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
