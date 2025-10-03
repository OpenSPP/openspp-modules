{
    "name": "CEL Registry Search",
    "summary": "Filter Registry (Individuals/Groups) using CEL expressions",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "author": "OpenSPP Community",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "category": "Tools",
    "depends": [
        "base",
        "g2p_registry_base",
        "spp_cel_domain",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/registrant_cel_filter_wizard_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
