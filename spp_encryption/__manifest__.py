# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "SPP Encryption",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "g2p_encryption",
    ],
    "external_dependencies": {"python": ["jwcrypto"]},
    "data": [
        "views/encryption_provider.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
