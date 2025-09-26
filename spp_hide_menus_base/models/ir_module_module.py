import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    # Map module technical names to menu xml_ids and icon paths
    MENU_APP = {
        "project_todo": {
            "menu_xml_id": "project_todo.menu_todo_todos",
        },
        "mail": {
            "menu_xml_id": "mail.menu_root_discuss",
        },
        "spreadsheet_dashboard": {
            "menu_xml_id": "spreadsheet_dashboard.spreadsheet_dashboard_menu_root",
        },
        "project": {
            "menu_xml_id": "project.menu_main_pm",
        },
        "mass_mailing": {
            "menu_xml_id": "mass_mailing.mass_mailing_menu_root",
        },
        "survey": {
            "menu_xml_id": "survey.menu_surveys",
        },
        "hr": {
            "menu_xml_id": "hr.menu_hr_root",
        },
        "calendar": {
            "menu_xml_id": "calendar.mail_menu_calendar",
        },
        "contacts": {
            "menu_xml_id": "contacts.menu_contacts",
        },
        "account": {
            "menu_xml_id": "account.menu_finance",
        },
        "event": {
            "menu_xml_id": "event.event_main_menu",
        },
        "stock": {
            "menu_xml_id": "stock.menu_stock_root",
        },
        "utm": {
            "menu_xml_id": "utm.menu_link_tracker_root",
        },
        "fastapi": {
            "menu_xml_id": "fastapi.menu_fastapi_root",
        },
    }

    def hide_menus(self):
        for module in self.search([]):
            menu_info = self.MENU_APP.get(module.name)
            if menu_info:
                try:
                    menu = self.env.ref(menu_info["menu_xml_id"])
                except ValueError:
                    menu = False

                if menu:
                    hidden_menus = self.env["spp.hide.menu"].search([("name", "=", menu.id)])
                    if not hidden_menus:
                        hidden_menu = self.env["spp.hide.menu"].create(
                            {
                                "name": menu.id,
                            }
                        )
                        hidden_menu.hide_menu()
                    elif hidden_menus.state == "show":
                        hidden_menus.hide_menu()

    def next(self):
        # Call your menu hiding logic first
        self.hide_menus()
        # Then call the original Odoo logic
        return super().next()
