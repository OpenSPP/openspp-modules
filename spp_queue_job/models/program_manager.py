import logging

from odoo import _, models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class DefaultProgramManager(models.Model):
    _inherit = "g2p.program.manager.default"

    def _enroll_eligible_registrants_async(self, states, members_count):
        self.ensure_one()
        _logger.debug("members: %s", members_count)
        program = self.program_id
        program.message_post(
            body=_("Eligibility check of %s beneficiaries started.", members_count)
        )
        program.write(
            {"locked": True, "locked_reason": "Eligibility check of beneficiaries"}
        )

        jobs = []
        for i in range(0, members_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(
                self.delayable(
                    channel="root_id_batch.channel_root_id_batch"
                )._enroll_eligible_registrants(states, i, self.MAX_ROW_JOB_QUEUE)
            )
        main_job = group(*jobs)
        main_job.on_done(
            self.delayable(
                channel="root_id_batch.channel_root_id_batch"
            ).mark_enroll_eligible_as_done()
        )
        main_job.delay()
