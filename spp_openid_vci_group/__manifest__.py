# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "SPP Registry OpenID VCI: Group",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "spp_openid_vci",
        "g2p_registry_group",
    ],
    "external_dependencies": {"python": ["qrcode"]},
    "data": [
        "views/group_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
