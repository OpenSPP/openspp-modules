# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Event Spec Loader",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123", "emjay0921"],
    "depends": [
        "base",
        "spp_event_data",
        "spp_base_common",
    ],
    "external_dependencies": {
        "python": ["pyyaml"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/program_spec_view.xml",
        "views/event_type_definition_view.xml",
        "views/menu_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "summary": "Dynamically generate event data types and components from YAML program specifications, enabling rapid deployment of event tracking for social protection programs.",
}
