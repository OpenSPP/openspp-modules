# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "Event Data: Program Membership",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": ["base", "spp_event_data", "g2p_programs"],
    "data": [
        "views/registrant_view.xml",
        "views/event_data_view.xml",
        "wizard/create_event_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
