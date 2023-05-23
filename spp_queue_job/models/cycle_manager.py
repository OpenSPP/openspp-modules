import logging

from odoo import _, models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class DefaultCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def _check_eligibility_async(self, cycle, beneficiaries_count):
        self.ensure_one()
        _logger.debug("Beneficiaries: %s", beneficiaries_count)
        cycle.message_post(
            body=_(
                "Eligibility check of %s beneficiaries started.", beneficiaries_count
            )
        )
        cycle.write(
            {"locked": True, "locked_reason": "Eligibility check of beneficiaries"}
        )

        jobs = []
        for i in range(0, beneficiaries_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(
                self.delayable(
                    channel="root_id_batch.channel_root_id_batch"
                )._check_eligibility(cycle, offset=i, limit=self.MAX_ROW_JOB_QUEUE)
            )
        main_job = group(*jobs)
        main_job.on_done(
            self.delayable(
                channel="root_id_batch.channel_root_id_batch"
            ).mark_check_eligibility_as_done(cycle)
        )
        main_job.delay()

    def _prepare_entitlements_async(self, cycle, beneficiaries_count):
        _logger.debug("Prepare entitlement asynchronously")
        cycle.message_post(
            body=_(
                "Prepare entitlement for %s beneficiaries started.", beneficiaries_count
            )
        )
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Prepare entitlement for beneficiaries."),
            }
        )

        jobs = []
        for i in range(0, beneficiaries_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(
                self.delayable(
                    channel="root_id_batch.channel_root_id_batch"
                )._prepare_entitlements(cycle, i, self.MAX_ROW_JOB_QUEUE)
            )
        main_job = group(*jobs)
        main_job.on_done(
            self.delayable(
                channel="root_id_batch.channel_root_id_batch"
            ).mark_prepare_entitlement_as_done(cycle, _("Entitlement Ready."))
        )
        main_job.delay()

    def _add_beneficiaries_async(self, cycle, beneficiaries, state):
        _logger.debug("Adding beneficiaries asynchronously")
        cycle.message_post(
            body="Import of %s beneficiaries started." % len(beneficiaries)
        )
        cycle.write({"locked": True, "locked_reason": _("Importing beneficiaries.")})

        beneficiaries_count = len(beneficiaries)
        jobs = []
        for i in range(0, beneficiaries_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(
                self.delayable(
                    channel="root_id_batch.channel_root_id_batch"
                )._add_beneficiaries(
                    cycle,
                    beneficiaries[i : i + self.MAX_ROW_JOB_QUEUE],
                    state,
                )
            )

        main_job = group(*jobs)
        main_job.on_done(
            self.delayable(
                channel="root_id_batch.channel_root_id_batch"
            ).mark_import_as_done(cycle, _("Beneficiary import finished."))
        )
        main_job.delay()
