from odoo import models


class SPPDMSFileCustom(models.Model):
    _inherit = "dms.file"

    def action_save_and_close(self):
        return {"type": "ir.actions.act_window_close"}
