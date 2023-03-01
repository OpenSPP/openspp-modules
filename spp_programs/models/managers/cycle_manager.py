from odoo import models


class CustomDefaultCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def on_start_date_change(self, cycle):
        pass
