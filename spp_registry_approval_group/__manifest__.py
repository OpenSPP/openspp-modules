# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Registry Approval: Group",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "summary": "Extending the OpenSPP registry's approval framework, this module enables formal validation and management of collective entity records. It integrates the existing workflow to ensure group data undergoes a structured review process, maintaining data integrity for program enrollment.",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["reichie020212"],
    "depends": [
        "spp_registry_approval",
    ],
    "data": [
        "views/groups_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
