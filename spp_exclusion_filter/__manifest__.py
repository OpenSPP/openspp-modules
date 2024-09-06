# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Exclusion Filter",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "spp_registry",
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
    "summary": "This module enhances the OpenSPP program creation process by enabling the configuration and application of exclusion filters, ensuring that only eligible registrants are considered for enrollment in new programs.",
}
