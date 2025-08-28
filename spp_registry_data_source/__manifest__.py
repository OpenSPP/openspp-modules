# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Data Source",
    "summary": "Establishes a secure framework for OpenSPP to connect with external data systems like national registries and social protection databases. It facilitates structured data retrieval, defines field mapping, configures secure authentication methods, and manages specific API endpoints.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
    ],
    "external_dependencies": {},
    "data": [
        "security/ir.model.access.csv",
        "views/data_source_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
