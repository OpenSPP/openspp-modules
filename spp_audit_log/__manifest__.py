# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "SPP Audit Log",
    "category": "OpenSPP",
    "version": "15.0.1.1.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "mail",
    ],
    "external_dependencies": {},
    "data": [
        "security/audit_log_security.xml",
        "security/ir.model.access.csv",
        "views/spp_audit_rule_views.xml",
        "views/spp_audit_log_views.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
