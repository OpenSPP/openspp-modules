{
    "name": """OpenSPP REST API: API Records""",
    "summary": """RESTful API routes for OpenSPP""",
    "category": "",
    "version": "15.0.0.0.0",
    "author": "OpenSPP.org",
    "development_status": "Alpha",
    "website": "https://github.com/openspp/openspp-program",
    "license": "LGPL-3",
    "depends": [
        "base",
        "spp_api",
        "spp_service_points",
        "uom",
    ],
    "data": [
        "data/spp_api_namespace_data.xml",
        "data/spp_api_path_data.xml",
        "views/uom_category_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
