# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP DCI API Server",
    "summary": "Exposes OpenSPP's individual and household registry data via a DCI-compliant RESTful API. Secures data exchange through client credential management and token-based authentication for external systems.",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "author": "OpenSPP.org",
    "development_status": "Production/Stable",
    "maintainers": [
        "jeremi",
        "gonzalesedwin1123",
        "reichie020212",
    ],
    "external_dependencies": {"python": ["PyLD", "pyjwt>=2.4.0"]},
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "spp_oauth",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/client_credentials_view.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
