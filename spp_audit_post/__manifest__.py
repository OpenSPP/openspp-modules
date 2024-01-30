# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "SPP Audit Post",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "mail",
        "spp_audit_log",
    ],
    "external_dependencies": {},
    "data": [
        "security/ir.model.access.csv",
        "views/spp_audit_rule_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
