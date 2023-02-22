import logging

from odoo import _, models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class CustomBaseCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def done_import(self, cycle, msg):
        self.ensure_one()
        if cycle.members_count == cycle.entitlements_count:
            cycle.write({"hide_prepare_entitlement_button": True})
        else:
            cycle.write({"hide_prepare_entitlement_button": False})

        cycle.locked = False
        cycle.locked_reason = None
        cycle.message_post(body=msg)
        return

    def _prepare_entitlements_async(self, cycle, beneficiaries_count):
        _logger.debug("Prepare entitlement asynchronously")
        cycle.write({"hide_prepare_entitlement_button": True})
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
        # Get the last iteration
        last_iter = int(beneficiaries_count / self.MAX_ROW_JOB_QUEUE) + (
            1 if (beneficiaries_count % self.MAX_ROW_JOB_QUEUE) > 0 else 0
        )
        ctr = 0
        for i in range(0, beneficiaries_count, self.MAX_ROW_JOB_QUEUE):
            ctr += 1
            if ctr == last_iter:
                # Last iteration, do not skip computing the total entitlements to update the total entitlement fields
                jobs.append(
                    self.delayable()._prepare_entitlements(
                        cycle, i, self.MAX_ROW_JOB_QUEUE, skip_count=False
                    )
                )
            else:
                jobs.append(
                    self.delayable()._prepare_entitlements(
                        cycle, i, self.MAX_ROW_JOB_QUEUE, skip_count=True
                    )
                )
        main_job = group(*jobs)
        main_job.on_done(self.delayable().done_import(cycle, _("Entitlement Ready.")))
        main_job.delay()

    def _prepare_entitlements(self, cycle, offset=0, limit=None, skip_count=False):
        super()._prepare_entitlements(
            cycle, offset=offset, limit=limit, skip_count=skip_count
        )

        cycle.write({"hide_prepare_entitlement_button": True})

        return
