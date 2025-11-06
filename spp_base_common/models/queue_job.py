# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class QueueJob(models.Model):
    """Extend queue.job to add res_id field for record tracking."""

    _inherit = "queue.job"

    res_id = fields.Integer(
        string="Record ID",
        help="ID of the record that created this job",
        index=True,
    )
    res_model = fields.Char(
        string="Record Model",
        help="Model name of the record that created this job",
        index=True,
    )
