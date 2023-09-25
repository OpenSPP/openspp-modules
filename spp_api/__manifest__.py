# Copyright 2018-2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """OpenSPP REST API""",
    "summary": """RESTful API for OpenSPP""",
    "category": "",
    "images": ["images/icon.png"],
    "version": "15.0.0.0.0",
    "application": False,
    "author": "OpenSPP.org",
    "development_status": "Alpha",
    "website": "https://github.com/openspp/openspp-program",
    "license": "LGPL-3",
    "depends": ["spp_base_api", "mail"],
    "external_dependencies": {
        "python": ["bravado_core", "swagger_spec_validator", "jsonschema"],
        "bin": [],
    },
    "data": [
        "security/openapi_security.xml",
        "security/ir.model.access.csv",
        "security/res_users_token.xml",
        "views/openapi_view.xml",
        "views/openapi_template.xml",
        "views/res_users_view.xml",
        "views/ir_model_view.xml",
        "views/spp_api_field_alias_views.xml",
    ],
    "demo": ["demo/openapi_demo.xml", "demo/openapi_security_demo.xml"],
    "post_load": "post_load",
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
}
