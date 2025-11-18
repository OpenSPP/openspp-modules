from odoo import fields, models


class OpenSPPAreaImport(models.Model):
    _inherit = "spp.area.import"

    job_ids = fields.One2many(
        "queue.job",
        compute="_compute_job_ids",
        string="Related Jobs",
        help="Queue jobs related to this area import",
    )

    def _compute_job_ids(self):
        """
        Compute related queue jobs based on res_id and res_model fields.
        """
        for rec in self:
            jobs = self.env["queue.job"].search(
                [
                    ("res_model", "=", "spp.area.import"),
                    ("res_id", "=", rec.id),
                ]
            )
            rec.job_ids = jobs
