from odoo import _, exceptions, fields, models
from odoo.addons.queue_job.job import DONE


class JobRelatedMixin(models.AbstractModel):
    """Mixin klass for queue.job relationship.

    Note that we support only 1 job at a time.
    If we want to support Queued Jobs, `queue.job.batch` will be needed.
    """

    _name = "g2p.job.mixin"
    _description = "Job Mixin"

    job_id = fields.Many2one("queue.job", string="Job", readonly=True)
    job_state = fields.Selection(index=True, related="job_id.state")
    job_type = fields.Char("Job Type", readonly=True)

    def has_job(self):
        return bool(self.job_id)

    def job_done(self):
        return self.job_state == DONE

    def can_create_new_job(self):
        if self.has_job() and not self.job_done():
            return False
        return True

    def _check_delete(self):
        if self.has_job() and not self.job_done():
            raise exceptions.Warning(_("You must complete the job first!"))

    def unlink(self):
        for item in self:
            item._check_delete()
        return super().unlink()
