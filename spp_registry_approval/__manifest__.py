# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

{
    "name": "OpenSPP Registry Approval: Base",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "summary": "This module implements a structured workflow for managing the lifecycle of OpenSPP registry entries, ensuring beneficiary data meets required standards through a formal approval process. It introduces distinct states for each entry and restricts approval actions to authorized personnel, preventing premature program enrollment.",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["reichie020212"],
    "depends": [
        "spp_registry_base",
    ],
    "data": [
        "security/security_access.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
