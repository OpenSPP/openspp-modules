# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DashBoardMenu(models.Model):
    _inherit = "dashboard.menu"

    sequence = fields.Integer(default=10)
    menu_id = fields.Many2one("ir.ui.menu", string="Parent Menu")
    action_menu_id = fields.Many2one("ir.ui.menu", string="Menu", ondelete="cascade")
    client_action = fields.Many2one("ir.actions.client", ondelete="cascade")

    @api.model
    def create(self, vals):
        """Override the create method to prevent automatic creation of actions menu."""
        return super().create(vals)

    @api.ondelete(at_uninstall=True)
    def _unlink_menu_action(self):
        """Override the delete method"""
        for rec in self:
            # Remove associated menu and client action
            if rec.client_action:
                rec.client_action.unlink()
            if rec.action_menu_id:
                rec.action_menu_id.unlink()

    @api.model
    def create_action_menu(self):
        for rec in self:
            values = {
                "name": rec.name,
                "tag": "dynamic_dashboard",
            }
            action_id = self.env["ir.actions.client"].create(values)
            client_action_id = action_id.id
            menu_id = self.env["ir.ui.menu"].create(
                {
                    "name": rec.name,
                    "parent_id": rec.menu_id.id,
                    "sequence": rec.sequence,
                    "action": "ir.actions.client,%d" % (action_id.id,),
                }
            )
            action_menu_id = menu_id.id
            rec.update(
                {
                    "menu_id": menu_id,
                    "client_action": client_action_id,
                    "action_menu_id": action_menu_id,
                }
            )
