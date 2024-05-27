{
    "name": """OpenSPP API: DCI Server""",
    "summary": """RESTful API routes for OpenSPP""",
    "category": "",
    "version": "17.0.1.0.0",
    "author": "OpenSPP.org",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "external_dependencies": {"python": ["PyLD", "pyjwt>=2.4.0"]},
    "website": "https://github.com/OpenSPP/openspp-modules",
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
