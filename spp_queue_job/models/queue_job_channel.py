from odoo import api, models


class CustomQueueJobChannel(models.Model):
    _inherit = "queue.job.channel"

    @api.constrains("parent_id", "name")
    def parent_required(self):
        pass
