# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Hide Non-OpenSPP Menus",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "summary": "The module automatically hides non-core OpenSPP menus to streamline the user interface. It removes Calendar, Contacts, Accounting, Event, Stock, and UTM from the main navigation, focusing users on social protection program management.",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "spp_hide_menus_base", "calendar", "contacts", "account", "event", "stock", "utm", "web"],
    "data": [
        "data/hide_menu_data.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
