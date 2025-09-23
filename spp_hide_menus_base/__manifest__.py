# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Hide Non-OpenSPP Menus: Base",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "summary": "Administrators can manage the visibility of OpenSPP navigation menus, streamlining the user interface for specific user groups. The module modifies ir.ui.menu records to control menu visibility, providing a foundation for other modules to selectively hide non-essential navigation items.",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["reichie020212"],
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/hide_menu_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
