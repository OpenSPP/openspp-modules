# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "SPP Program: Manual Eligibility",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "spp_registry",
        "g2p_programs",
        "spp_programs",
    ],
    "data": [
        "views/program_view.xml",
        "views/program_membership_view.xml",
        "wizard/create_program_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
