# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Registry Group Hierarchy",
    "summary": "Introduces hierarchical relationships between groups, allowing for nested group structures within social protection programs and farmer registries.",
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
        "spp_registry",
    ],
    "external_dependencies": {},
    "data": [
        "views/group_kind_views.xml",
        "views/group_membership_views.xml",
        "views/group_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
