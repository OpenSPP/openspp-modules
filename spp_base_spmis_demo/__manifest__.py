# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP SPMIS Demo",
    "summary": "Generates and populates the OpenSPP SPMIS Base with comprehensive, realistic sample data. It integrates with core registry models to provide diverse registrant profiles and social protection data, facilitating system exploration, training, and testing.",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "external_dependencies": {"python": ["faker"]},
    "maintainers": ["jeremi", "gonzalesedwin1123", "emjay0921"],
    "depends": [
        "base",
        "g2p_registry_base",
        "spp_base_spmis",
        "spp_demo_common",
        "queue_job",
    ],
    "excludes": [
        "spp_base_farmer_registry",
        "spp_base_social_registry",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
