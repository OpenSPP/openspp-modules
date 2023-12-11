# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Programs: Compliance Criteria",
    "category": "OpenSPP",
    "version": "15.0.0.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_programs",
        "spp_area",
        "spp_programs",
        "spp_eligibility_sql",
        "spp_eligibility_tags",
        "web_domain_field",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/g2p_cycle_views.xml",
        "views/g2p_program_views.xml",
        "views/res_config_settings_views.xml",
        "wizards/g2p_program_create_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "spp_programs_compliance_criteria/static/src/js/field_domain.js",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}
