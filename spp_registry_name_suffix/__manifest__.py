# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Registry Name Suffix",
    "summary": "Adds a configurable suffix field (Jr., Sr., III, etc.) to Individual registrant names in OpenSPP.",
    "category": "OpenSPP",
    "version": "17.0.1.4.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "spp_registrant_import",
        "g2p_registry_individual",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/name_suffix_views.xml",
        "views/res_partner_views.xml",
        "data/name_suffix_data.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
