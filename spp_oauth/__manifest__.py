{
    "name": "OpenSPP API: Oauth",
    "summary": "Provides OAuth 2.0 authentication for secure access to the OpenSPP API.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "author": "OpenSPP.org",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "external_dependencies": {"python": ["pyjwt>=2.4.0"]},
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "data/ir_config_parameter_data.xml",
        "views/res_config_view.xml",
        "views/ir_config_parameter_view.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
