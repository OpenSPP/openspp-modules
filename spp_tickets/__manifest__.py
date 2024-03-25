{
    "name": "OpenSPP Ticketing System",
    "version": "1.0",
    "summary": "Ticketing System for OpenSPP",
    "sequence": 10,
    "description": """Manage inquiries, requests, and reports efficiently.""",
    "category": "Services",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/spp_ticket_views.xml",
        "views/res_partner_views.xml",
        "views/spp_ticket_tag_views.xml",
        "data/spp_ticket_data.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
