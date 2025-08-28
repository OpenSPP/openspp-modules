# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Exclusion Filter",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_programs",
        "spp_programs",
    ],
    "data": [
        "wizard/create_program_wizard.xml",
        "views/managers/eligibility_manager_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
    "summary": "Administrators can define and apply specific exclusion criteria based on registrant attributes or existing program participation. The module automates eligibility checks during program creation, systematically filtering out ineligible individuals to refine the beneficiary pool.",
}
