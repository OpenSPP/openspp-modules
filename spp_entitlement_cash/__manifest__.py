# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Cash Entitlement",
    "summary": "Manage cash-based entitlements for beneficiaries within social protection programs, including defining calculation rules, automating disbursement, and tracking payments.",
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
