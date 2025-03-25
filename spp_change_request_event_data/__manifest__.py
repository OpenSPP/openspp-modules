{
    "name": "OpenSPP Change Request Event Data",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["shashikala1998"],
    "depends": [
        "spp_event_data",
        "spp_change_request",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/change_request_view.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
