import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    # Map module technical names to menu xml_ids and icon paths
    ICON_MAP = {
        'project_todo': {
            'menu_xml_id': 'project_todo.menu_todo_todos',
            'icon': 'spp_registry_base,static/description/icon-To-do-White-line.png',
        },
        'mail': {
            'menu_xml_id': 'mail.menu_root_discuss',
            'icon': 'spp_registry_base,static/description/icon-Discuss-White-line.png',
        },
        'queue_job': {
            'menu_xml_id': 'queue_job.menu_queue_job_root',
            'icon': 'spp_registry_base,static/description/icon-Job-Queue-White-line.png',
        },
        'spreadsheet_dashboard': {
            'menu_xml_id': 'spreadsheet_dashboard.spreadsheet_dashboard_menu_root',
            'icon': 'spp_registry_base,static/description/icon-Dashboards-White-line.png',
        },
        'project': {
            'menu_xml_id': 'project.menu_main_pm',
            'icon': 'spp_registry_base,static/description/icon-Project-White-line.png',
        },
        'mass_mailing': {
            'menu_xml_id': 'mass_mailing.mass_mailing_menu_root',
            'icon': 'spp_registry_base,static/description/icon-Email-Marketing-White-line.png',
        },
        'survey': {
            'menu_xml_id': 'survey.menu_surveys',
            'icon': 'spp_registry_base,static/description/icon-Surveys-White-line.png',
        },
        'hr': {
            'menu_xml_id': 'hr.menu_hr_root',
            'icon': 'spp_registry_base,static/description/icon-Employees-White-line.png',
        },
        # Add more modules as needed
    }
    
    def update_menu_icons(self):
        for module in self.search([]):
            icon_info = self.ICON_MAP.get(module.name)
            if icon_info:
                try:
                    menu = self.env.ref(icon_info['menu_xml_id'])
                except ValueError:
                    menu = False

                if menu:
                    menu.write({'web_icon': icon_info['icon']})
                    _logger.info(
                        "Updated icon for menu '%s' (module '%s') to '%s'",
                        icon_info['menu_xml_id'], module.name, icon_info['icon']
                    )
                else:
                    _logger.warning(
                        "Menu with xml_id '%s' not found for module '%s'",
                        icon_info['menu_xml_id'], module.name
                    )

    def next(self):
        # Call your icon update logic first
        self.update_menu_icons()
        # Then call the original Odoo logic
        return super().next()