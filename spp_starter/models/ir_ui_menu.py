from odoo import api, models, tools
from odoo.tools.safe_eval import safe_eval


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "debug")
    def _visible_menu_ids(self, debug=False):
        menus = super()._visible_menu_ids(debug)
        show_spp_starter = safe_eval(
            self.env["ir.config_parameter"].sudo().get_param("spp_starter.show_spp_starter", "True")
        )
        if show_spp_starter:
            menu_item_id = self.env.ref("base.menu_management").id
        else:
            menu_item_id = self.env.ref("spp_starter.spp_starter_menu").id
        menus.discard(menu_item_id)
        return menus
