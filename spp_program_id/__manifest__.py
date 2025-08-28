# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Program ID",
    "summary": "Assigns and manages unique, immutable identifiers for every social protection program within the OpenSPP platform. This core component extends program records to ensure distinct identification, facilitating streamlined data management, enhanced reporting, and seamless system integration.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "nhatnm0612"],
    "depends": [
        "spp_programs",
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "views/g2p_program_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
