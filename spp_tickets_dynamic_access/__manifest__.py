# dynamic_partner_access/__manifest__.py
{
    "name": "Dynamic Partner Access Based on Ticket Assignment",
    "version": "1.0",
    "summary": "Manage dynamic access to partners based on ticket assignments.",
    "sequence": -100,
    "description": """This module provides dynamic access control for support staff to partner records based on ticket
    assignments.""",
    "category": "Custom Development",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "security/ir.model.access.csv",  # Ensure this is included
        "views/res_partner_views.xml",  # You'll create this to add the support_staff_ids field to the UI
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
