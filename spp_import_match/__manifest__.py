# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Import Match",
    "summary": "OpenSPP Import Match enhances data import processes by intelligently matching incoming records against existing data, preventing duplication and ensuring registry integrity. It provides configurable matching logic and supports seamless updates to existing records during bulk data onboarding.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "spp_registry_base", "base_import", "queue_job"],
    "data": [
        "data/queue_job_data.xml",
        "security/ir.model.access.csv",
        "views/import_match_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/spp_import_match/static/src/legacy/js/custom_base_import.js",
        ],
        "web.assets_qweb": [
            "spp_import_match/static/src/legacy/xml/custom_base_import.xml",
        ],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
