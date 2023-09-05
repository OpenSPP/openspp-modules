# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Programs: Import",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-program",
    "license": "LGPL-3",
    "development_status": "Alpha",
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
