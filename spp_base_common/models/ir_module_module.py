import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    # Map module technical names to menu xml_ids and icon paths
    ICON_MAP = {
        "project_todo": {
            "menu_xml_id": "project_todo.menu_todo_todos",
            "icon": "spp_base_common,static/description/icon-To-do-White-line.png",
        },
        "mail": {
            "menu_xml_id": "mail.menu_root_discuss",
            "icon": "spp_base_common,static/description/icon-Discuss-White-line.png",
        },
        "queue_job": {
            "menu_xml_id": "queue_job.menu_queue_job_root",
            "icon": "spp_base_common,static/description/icon-Job-Queue-White-line.png",
        },
        "spreadsheet_dashboard": {
            "menu_xml_id": "spreadsheet_dashboard.spreadsheet_dashboard_menu_root",
            "icon": "spp_base_common,static/description/icon-Dashboards-White-line.png",
        },
        "project": {
            "menu_xml_id": "project.menu_main_pm",
            "icon": "spp_base_common,static/description/icon-Project-White-line.png",
        },
        "mass_mailing": {
            "menu_xml_id": "mass_mailing.mass_mailing_menu_root",
            "icon": "spp_base_common,static/description/icon-Email-Marketing-White-line.png",
        },
        "survey": {
            "menu_xml_id": "survey.menu_surveys",
            "icon": "spp_base_common,static/description/icon-Surveys-White-line.png",
        },
        "hr": {
            "menu_xml_id": "hr.menu_hr_root",
            "icon": "spp_base_common,static/description/icon-Employees-White-line.png",
        },
        "calendar": {
            "menu_xml_id": "calendar.mail_menu_calendar",
            "icon": "spp_base_common,static/description/OpenSPP-Icons-Menu-Calendar.png",
        },
        "contacts": {
            "menu_xml_id": "contacts.menu_contacts",
            "icon": "spp_base_common,static/description/OpenSPP-Icons-Menu-Contacts.png",
        },
        "account": {
            "menu_xml_id": "account.menu_finance",
            "icon": "spp_base_common,static/description/OpenSPP-Icons-Menu-Invoicing.png",
        },
        "event": {
            "menu_xml_id": "event.event_main_menu",
            "icon": "spp_base_common,static/description/OpenSPP-Icons-Menu-Events.png",
        },
        "stock": {
            "menu_xml_id": "stock.menu_stock_root",
            "icon": "spp_base_common,static/description/OpenSPP-Icons-Menu-Inventory.png",
        },
        "utm": {
            "menu_xml_id": "utm.menu_link_tracker_root",
            "icon": "spp_base_common,static/description/OpenSPP-Icons-Menu-Link-Tracker.png",
        },
        "fastapi": {
            "menu_xml_id": "fastapi.menu_fastapi_root",
            "icon": "spp_base_common,static/description/icon-fast-api.png",
        },
    }

    def update_menu_icons(self):
        for module in self.search([]):
            icon_info = self.ICON_MAP.get(module.name)
            if icon_info:
                try:
                    menu = self.env.ref(icon_info["menu_xml_id"])
                except ValueError:
                    menu = False

                if menu:
                    menu.write({"web_icon": icon_info["icon"]})

    def next(self):
        # Call your icon update logic first
        self.update_menu_icons()
        # Then call the original Odoo logic
        return super().next()
