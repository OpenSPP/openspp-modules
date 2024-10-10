from odoo import models


class DefaultCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    # def new_cycle(self, name, new_start_date, sequence):
    #     for rec in self:
    #         cycle = super(DefaultCycleManager, rec).new_cycle(name, new_start_date, sequence)
    #         cycle.write({
    #             'from_date': cycle.start_date,
    #             'to_date': cycle.end_date,
    #         })
    #         return cycle
