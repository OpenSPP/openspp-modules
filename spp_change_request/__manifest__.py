# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Change Request",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp-project/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "external_dependencies": {
        "python": [
            "python-magic",
        ]
    },
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "dms_field",
    ],
    "data": [
        "security/change_request_security.xml",
        "security/ir.model.access.csv",
        "data/sequences.xml",
        "data/mail_activity.xml",
        "data/dms.xml",
        "views/main_view.xml",
        "views/change_request_view.xml",
        "views/change_request_validation_sequence_view.xml",
        "views/types/change_request_add_children_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_change_request/static/src/scss/change_request.scss",
        ],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
