# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "SPP Program Entitlement (Cash)",
    "category": "SPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_programs",
        "spp_programs",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/entitlement_manager_view.xml",
        "wizard/create_program_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
