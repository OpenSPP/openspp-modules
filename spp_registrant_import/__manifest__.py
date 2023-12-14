# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP: Import Improvement",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123", "nhatnm0612"],
    "depends": [
        "spp_base",
        "spp_import_match",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/spp_area_views.xml",
        "views/spp_service_point_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
