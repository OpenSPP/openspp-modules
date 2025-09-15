# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


{
    "name": "OpenSPP Event Demo",
    "summary": "OpenSPP Event Demo offers predefined event types, data models, and user interfaces for tracking specific social protection program interactions. It extends registrant profiles to display active event statuses and serves as a practical blueprint for custom event type implementation, leveraging the spp_event_data framework.",
    "category": "OpenSPP",
    "version": "17.0.1.3.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123", "emjay0921"],
    "depends": ["base", "spp_event_data"],
    "data": [
        "security/ir.model.access.csv",
        "views/house_visit_view.xml",
        "views/phone_survey_view.xml",
        "views/registrant_view.xml",
        "wizard/create_event_house_visit_wizard.xml",
        "wizard/create_event_phone_survey_wizard.xml",
        "wizard/create_event_school_enrolment_wizard.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
