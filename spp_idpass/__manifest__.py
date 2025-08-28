# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "ID PASS",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "summary": "OpenSPP Idpass securely generates and manages digital identification passes for program registrants, streamlining beneficiary verification and access to social protection services. The module automates ID generation using existing registrant data, offers configurable templates with expiry rules, and integrates with external services via secure API calls.",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "g2p_registry_base", "g2p_registry_membership"],
    "data": [
        "data/id_pass.xml",
        "views/main_view.xml",
        "views/registrant.xml",
        "security/ir.model.access.csv",
        "views/id_pass_view.xml",
        "views/id_type.xml",
        "wizard/issue_id_pass_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
