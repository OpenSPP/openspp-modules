# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Custom Fields",
    "summary": "The module enables administrators to define and add custom data fields directly to registrant profiles, tailoring data collection for specific social protection programs. It supports field differentiation by registrant type, integrates new data points into records, and provides dedicated sections for read-only program indicators.",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "g2p_registry_base"],
    "data": [
        "security/ir.model.access.csv",
        "views/field_group_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
