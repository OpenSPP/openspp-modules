# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Auto-Update Entitlements",
    "summary": "Automatically reviews and updates the state of entitlements based on their redemption status at the end of each program cycle. It assigns precise states, including a new 'Partially Redeemed' status, to ensure accurate records for program closure, reporting, and auditing.",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_programs",
        "spp_programs",
        "spp_ent_trans",
    ],
    "data": [
        "views/cycle_view.xml",
        "views/entitlements_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
