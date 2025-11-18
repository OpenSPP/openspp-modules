from odoo import api, fields, models


class OpenSPPAreaImport(models.Model):
    _inherit = "spp.area.import"

    job_ids = fields.One2many(
        "queue.job",
        compute="_compute_job_ids",
        string="Related Jobs",
        help="Queue jobs related to this area import",
    )

    has_ongoing_jobs = fields.Boolean(
        compute="_compute_has_ongoing_jobs",
        string="Has Ongoing Jobs",
        help="True if there are any ongoing queue jobs for this model",
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

    @api.depends("job_ids", "job_ids.state")
    def _compute_has_ongoing_jobs(self):
        """
        Check if there are any ongoing jobs for the spp.area.import model.
        This checks across ALL area import records to prevent concurrent operations.
        """
        # Check for any ongoing jobs for the entire model
        ongoing_jobs_count = self.env["queue.job"].search_count(
            [
                ("res_model", "=", "spp.area.import"),
                ("state", "in", ["pending", "enqueued", "started"]),
            ]
        )
        has_ongoing = ongoing_jobs_count > 0

        # Set the same value for all records
        for rec in self:
            rec.has_ongoing_jobs = has_ongoing
