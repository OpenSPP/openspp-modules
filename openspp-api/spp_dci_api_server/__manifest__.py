{
    "name": """OpenSPP API: DCI Server""",
    "summary": """RESTful API routes for OpenSPP""",
    "category": "",
    "version": "15.0.0.0.0",
    "author": "OpenSPP.org",
    "development_status": "Alpha",
    "external_dependencies": {"python": ["PyLD", "pyjwt>=2.4.0"]},
    "website": "https://github.com/openspp/openspp-program",
    "license": "LGPL-3",
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_individual",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/client_credentials_view.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
