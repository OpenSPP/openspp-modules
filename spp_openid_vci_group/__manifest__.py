# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP OpenID VCI Group",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
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
    "summary": "Extends OpenSPP's Verifiable Credential issuance capabilities to manage and represent groups of registrants. Generates standardized VCs encapsulating group information from registry data, providing a verifiable digital identity for efficient verification and integration with group management.",
}
