# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Job Queue",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "queue_job",
        "g2p_registry_base",
        "spp_idpass",
        "spp_idqueue",
        "spp_programs",
    ],
    "data": [
        "data/queue_data.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
