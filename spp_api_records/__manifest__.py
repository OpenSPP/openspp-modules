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
        "spp_api",
        "spp_service_points",
        "spp_service_point_device",
    ],
    "data": [
        "data/spp_api_namespace_data.xml",
        "data/spp_api_path_data.xml",
<<<<<<< HEAD
=======
        "views/spp_service_point_device_views.xml",
        "views/spp_service_point_views.xml",
        "security/ir.model.access.csv",
>>>>>>> 030b079 ([UPD] add model, views, tests for terminal devices)
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
