{
    "name": """OpenSPP Import: CRVS Beneficiaries""",
    "summary": """RESTful API routes for OpenSPP""",
    "category": "",
    "version": "15.0.0.0.0",
    "author": "OpenSPP.org",
    "development_status": "Alpha",
    "external_dependencies": {
        "python": [
            "PyLD",
        ]
    },
    "website": "https://github.com/openspp/openspp-program",
    "license": "LGPL-3",
    "depends": [
        "base",
        "g2p_programs",
        "spp_programs",
        "g2p_registry_base",
        "g2p_registry_individual",
    ],
    "data": [
        "security/fetch_crvs_security.xml",
        "security/ir.model.access.csv",
        "views/create_program_wizard_view.xml",
        "views/eligibility_manager_view.xml",
        "views/fetch_crvs_beneficiary_views.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
