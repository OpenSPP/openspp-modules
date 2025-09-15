# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Dashboard: Base",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "summary": "Establishes the foundational framework and consistent user interface components for analytical dashboards across the OpenSPP platform. It delivers core data visualization elements, including reusable metrics, charts, and data cards, enabling other modules to build specialized program-specific dashboards.",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["reichie020212"],
    "depends": [
        "base",
    ],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "spp_dashboard_base/static/src/dashboard/**/*",
            "spp_dashboard_base/static/src/chart/**/*",
            "spp_dashboard_base/static/src/card_board/**/*",
        ],
    },
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
