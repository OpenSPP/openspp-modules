import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    # Map module technical names to menu xml_ids and icon paths
    ICON_MAP = {
        "project_todo": {
            "menu_xml_id": "project_todo.menu_todo_todos",
            "icon": "spp_base_common,static/description/openspp-icons-menu-to-do.png",
        },
        "mail": {
            "menu_xml_id": "mail.menu_root_discuss",
            "icon": "spp_base_common,static/description/openspp-icons-menu-discuss.png",
        },
        "queue_job": {
            "menu_xml_id": "queue_job.menu_queue_job_root",
            "icon": "spp_base_common,static/description/openspp-icons-menu-job-queue.png",
        },
        "spreadsheet_dashboard": {
            "menu_xml_id": "spreadsheet_dashboard.spreadsheet_dashboard_menu_root",
            "icon": "spp_base_common,static/description/openspp-icons-menu-dashboards.png",
        },
        "project": {
            "menu_xml_id": "project.menu_main_pm",
            "icon": "spp_base_common,static/description/openspp-icons-menu-project.png",
        },
        "mass_mailing": {
            "menu_xml_id": "mass_mailing.mass_mailing_menu_root",
            "icon": "spp_base_common,static/description/openspp-icons-menu-email-marketing.png",
        },
        "survey": {
            "menu_xml_id": "survey.menu_surveys",
            "icon": "spp_base_common,static/description/openspp-icons-menu-surveys.png",
        },
        "hr": {
            "menu_xml_id": "hr.menu_hr_root",
            "icon": "spp_base_common,static/description/openspp-icons-menu-employees.png",
        },
        "calendar": {
            "menu_xml_id": "calendar.mail_menu_calendar",
            "icon": "spp_base_common,static/description/openspp-icons-menu-calendar.png",
        },
        "contacts": {
            "menu_xml_id": "contacts.menu_contacts",
            "icon": "spp_base_common,static/description/openspp-icons-menu-contacts.png",
        },
        "account": {
            "menu_xml_id": "account.menu_finance",
            "icon": "spp_base_common,static/description/openspp-icons-menu-invoicing.png",
        },
        "event": {
            "menu_xml_id": "event.event_main_menu",
            "icon": "spp_base_common,static/description/openspp-icons-menu-events.png",
        },
        "stock": {
            "menu_xml_id": "stock.menu_stock_root",
            "icon": "spp_base_common,static/description/openspp-icons-menu-inventory.png",
        },
        "utm": {
            "menu_xml_id": "utm.menu_link_tracker_root",
            "icon": "spp_base_common,static/description/openspp-icons-menu-link-tracker.png",
        },
        "fastapi": {
            "menu_xml_id": "fastapi.menu_fastapi_root",
            "icon": "spp_base_common,static/description/openspp-icons-menu-fast-api.png",
        },
        "spp_grm": {
            "menu_xml_id": "spp_grm.spp_grm_ticket_main_menu",
            "icon": "spp_base_common,static/description/openspp-icons-menu-helpdesk.png",
        },
        "point_of_sale": {
            "menu_xml_id": "point_of_sale.menu_point_root",
            "icon": "spp_base_common,static/description/openspp-icons-menu-point-of-sale.png",
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
