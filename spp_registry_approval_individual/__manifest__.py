# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Registry Approval: Individual",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "summary": "Manages the validation and official status of individual registrants by extending the base registry approval process within social protection programs. It ensures individual beneficiary data undergoes a dedicated review workflow, applying core approval states to enhance data quality and enable precise program enrollment.",
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
        "views/individuals_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
