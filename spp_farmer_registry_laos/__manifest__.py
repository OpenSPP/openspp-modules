# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Farmer Registry: Laos",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "external_dependencies": {"python": ["faker"]},
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_registry_base",
        "spp_farmer_registry_base",
        "spp_event_data",
        "queue_job",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/group_view.xml",
        "views/event_data_view.xml",
        "views/generate_farmer_data_view.xml",
        "views/laos_raster_view.xml",
        "wizard/create_event_farm_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
