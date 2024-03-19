# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "SPP Document Management System",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
    ],
    "external_dependencies": {"python": ["PIL"]},
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/main_view.xml",
        "views/dms_directory_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
