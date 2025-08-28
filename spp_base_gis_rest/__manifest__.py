# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Base GIS REST",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": ["spp_base_gis", "spp_oauth"],
    "data": [
        "security/ir.model.access.csv",
        "views/api_client_credentials_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "The module provides RESTful API endpoints for secure, programmatic access to OpenSPP's Geographical Information System data, leveraging OAuth 2. 0 and Basic authentication.",
}
