# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Farmer Registry Base",
    "summary": "Base module for managing farmer registries, linking farmers to farms, land, and agricultural activities.",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_registry_membership",
        "spp_base_gis",
        "spp_land_record",
        "base_import",
    ],
    "external_dependencies": {"python": ["shapely", "geojson", "simplejson", "pyproj"]},
    "data": [
        "security/ir.model.access.csv",
        "data/kind_data.xml",
        "data/id_data.xml",
        "views/res_partner.xml",
        "views/configuration_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
