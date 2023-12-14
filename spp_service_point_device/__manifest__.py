# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Service Point Device",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "spp_service_points",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/spp_service_point_device_views.xml",
        "views/spp_service_point_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
