import logging

from odoo import models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class DefaultEligibilityManager(models.Model):
    _inherit = "g2p.program_membership.manager.default"

    def _import_registrants_async(self, new_beneficiaries, state="draft"):
        self.ensure_one()
        program = self.program_id
        program.message_post(
            body="Import of %s beneficiaries started." % len(new_beneficiaries)
        )
        program.write({"locked": True, "locked_reason": "Importing beneficiaries"})

        jobs = []
        for i in range(0, len(new_beneficiaries), 10000):
            jobs.append(
                self.delayable(
                    channel="root_id_batch.channel_root_id_batch"
                )._import_registrants(new_beneficiaries[i : i + 10000], state)
            )
        main_job = group(*jobs)
        main_job.on_done(
            self.delayable(
                channel="root_id_batch.channel_root_id_batch"
            ).mark_import_as_done()
        )
        main_job.delay()
