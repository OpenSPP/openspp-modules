# Copyright (C) 2025 OpenSPP contributors
{
    "name": "OpenSPP Metrics UI for Registrants",
    "summary": "Adds Metrics smart button on Individuals/Groups (res.partner) to view related metric values.",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "author": "OpenSPP",
    "category": "Tools",
    "depends": ["contacts", "spp_indicators", "g2p_registry_individual", "g2p_registry_group"],
    "data": [
        "views/refresh_wizard_views.xml",
        "views/feature_value_views.xml",
        "views/res_partner_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
