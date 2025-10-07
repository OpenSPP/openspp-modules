# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Irrigation",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "spp_base_gis",
    ],
    "data": [
        "security/irrigation_security.xml",
        "security/ir.model.access.csv",
        "views/irrigation_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "Manages detailed irrigation assets by type, capacity, and unique identifiers, leveraging integrated GIS capabilities to map and display infrastructure locations and boundaries. The module models water distribution networks by defining and linking irrigation sources to destinations, providing critical data for strategic planning of resource allocation and infrastructure projects.",
}
