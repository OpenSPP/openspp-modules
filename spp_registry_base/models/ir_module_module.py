import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    # Map module technical names to menu xml_ids and icon paths
    ICON_MAP = {
        'survey': {
            'menu_xml_id': 'survey.menu_surveys',
            'icon': 'spp_registry_base,static/description/icon-Surveys-White-line.png',
        },
        # Add more modules as needed
    }

    @api.model
    def button_install(self):
        res = super().button_install()
        for module in self:
            icon_info = self.ICON_MAP.get(module.name)
            if icon_info:
                menu = self.env['ir.ui.menu'].search([('xml_id', '=', icon_info['menu_xml_id'])], limit=1)
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
        return res