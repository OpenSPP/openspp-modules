{
    "name": "OpenSPP Theme (Muk Theme)",
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-modules",
    "category": "Theme",
    "version": "17.0.1.0.0",
    "depends": ["web", "muk_web_theme"],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "data": [],
    "assets": {
        "web._assets_primary_variables": [
            "theme_openspp_muk/static/src/scss/colors.scss",
            "theme_openspp_muk/static/src/scss/colors_light.scss",
        ],
        "web.assets_web_dark": ["theme_openspp_muk/static/src/scss/colors_dark.scss"],
        "web.assets_backend": ["theme_openspp_muk/static/src/scss/navbar.scss"],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
