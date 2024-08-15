{
    "name": "OpenSPP API Records",
    "summary": """Provides RESTful API endpoints for accessing and managing OpenSPP's core data, including service points, programs, products, and entitlements.""",
    "category": "",
    "version": "17.0.1.0.0",
    "author": "OpenSPP.org",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "depends": [
        "base",
        "spp_api",
        "spp_service_points",
        "uom",
        "spp_service_point_device",
        "product",
        "g2p_programs",
        "spp_programs",
        "spp_entitlement_cash",
        "spp_entitlement_in_kind",
        "spp_ent_trans",
        "contacts",
        "g2p_registry_base",
        "spp_area",
        "spp_programs_sp",
    ],
    "data": [
        "data/spp_api_namespace_data.xml",
        "data/spp_api_path_data.xml",
        "views/spp_service_point_views.xml",
        "views/uom_category_views.xml",
        "data/spp_api_field_data.xml",
        "data/spp_api_field_alias_data.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
