# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Registry Search",
    "category": "OpenSPP/OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "emjay0921"],
    "depends": [
        "base",
        "g2p_registry_base",
        "spp_base_common",
        "g2p_registry_individual",
        "g2p_registry_group",
    ],
    "excludes": [],
    "external_dependencies": {},
    "data": [
        "security/ir.model.access.csv",
        "data/partner_search_field_data.xml",
        "views/partner_search_field_view.xml",
        "views/partner_custom_search_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_registry_search/static/src/js/partner_search_view.js",
            "spp_registry_search/static/src/js/partner_search_widget.js",
            "spp_registry_search/static/src/xml/partner_search_view.xml",
            "spp_registry_search/static/src/xml/partner_search_widget.xml",
        ],
    },
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
    "summary": "Provides advanced search capabilities for the OpenSPP Registry. Features include configurable search fields, dynamic field filtering by registrant type (Individual/Group), and an intuitive search interface with real-time results.",
}
