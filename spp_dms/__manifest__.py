# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Document Management System",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "web",
    ],
    "external_dependencies": {"python": ["Pillow>=9.0.1"]},
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/main_view.xml",
        "views/dms_directory_views.xml",
        "views/dms_file_views.xml",
        "views/dms_category_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_dms/static/src/js/preview_binary_field.esm.js",
            "spp_dms/static/src/xml/preview_binary_field.xml",
        ],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "The OpenSPP Dms module provides a centralized system for managing and organizing program-related documents within a structured directory tree. It facilitates efficient document retrieval through categorization and indexed storage, automatically capturing essential file metadata such as size, type, and data integrity checksums.",
}
