from datetime import datetime

from odoo import _, models

from odoo.addons.queue_job.delay import group


class OpenSPPPrintBatch(models.Model):
    _inherit = "spp.print.queue.batch"

    def _generate_batch(self, batch_ids):
        """
        This function is used to generate cards from batch by
        creating a Queue Job for each Job Batch
        :param batch_ids: The Batch IDS.
        :return: Return a notification to state the progress
        """
        ctr_batch = 0
        ctr_ids = 0
        for rec in batch_ids:
            ctr_batch += 1
            rec.status = "generating"
            queued_ids = []
            jobs = []
            max_rec = len(rec.queued_ids)
            for ctr, queued_id in enumerate(rec.queued_ids, 1):
                queued_id.status = "generating"
                message = _("{} started to generate this request on {}.").format(
                    self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
                )
                queued_id.save_to_mail_thread(message)
                ctr_ids += 1
                queued_ids.append(queued_id.id)
                if (ctr % self.JOBBATCH_SIZE == 0) or ctr == max_rec:
                    jobs.append(
                        rec.delayable(
                            channel="root_id_batch.channel_root_id_batch"
                        )._generate_cards(queued_ids)
                    )
                    queued_ids = []

            main_job = group(*jobs)
            main_job.on_done(
                self.delayable(
                    channel="root_id_batch.channel_root_id_batch"
                ).mark_as_done(rec)
            )
            main_job.delay()

            message_1 = _("{} started to generate this batch on {}.").format(
                self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
            )
            rec.save_to_mail_thread(message_1)

        message = _("{} Batch(es) with total of {} IDs are being generated.").format(
            ctr_batch or "", ctr_ids or ""
        )
        kind = "info"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ID Batch"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }
