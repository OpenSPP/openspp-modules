# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Base (Common)",
    "category": "OpenSPP/OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "emjay0921"],
    "depends": [
        "base",
        "queue_job",
        "theme_openspp_muk",
        "spp_user_roles",
        "spp_area_base",
        "spp_hide_menus_base",
        "spp_base_setting",
        "g2p_registry_base",
    ],
    "excludes": [],
    "external_dependencies": {},
    "data": [
        "data/global_roles.xml",
        "data/local_roles.xml",
        "security/security_access.xml",
        "security/ir.model.access.csv",
        "views/main_view.xml",
        "views/phone_validation_view.xml",
        "views/queue_job_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_base_common/static/src/scss/navbar.scss",
        ],
        "web._assets_primary_variables": [
            "spp_base_common/static/src/scss/colors.scss",
            "spp_base_common/static/src/scss/colors_light.scss",
        ],
        "web.assets_web_dark": ["spp_base_common/static/src/scss/colors_dark.scss"],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "The OpenSPP base module that provides the main menu, generic configuration, user role management base module, area management base module, hiding of non-openspp menus, and theme. All implementation specific base modules depends on this module.",
}
