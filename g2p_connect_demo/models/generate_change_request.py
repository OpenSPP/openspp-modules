# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging
import math

from odoo import api, fields, models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class OpenG2PGenerateChangeRequestData(models.Model):
    _name = "g2p.generate.change.request.data"

    name = fields.Char()
    num_crs = fields.Integer("Number of CRs", default=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("generate", "Generated"),
        ],
        default="draft",
    )

    def generate_sample_data(self):

        batches = math.ceil(self.num_crs / 1000)
        jobs = []
        for _i in range(0, batches):
            jobs.append(self.delayable()._generate_sample_data(res_id=self.id))
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_as_done())
        main_job.delay()

    @api.model
    def _generate_sample_data(self, **kwargs):
        """
        Generate sample data for testing
        Returns:
        """

    def mark_as_done(self):
        self.update({"state": "generate"})
