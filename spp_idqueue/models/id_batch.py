# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


import json
from datetime import date, datetime

import requests

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group


class OpenSPPPrintBatch(models.Model):
    _name = "spp.print.queue.batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "ID print Batch"
    _order = "id DESC"

    JOBBATCH_SIZE = 20

    name = fields.Char("Batch name")

    #  We should only allow `approved` id to be added to a batch
    queued_ids = fields.One2many("spp.print.queue.id", "batch_id", string="Queued IDs")
    status = fields.Selection(
        [
            ("new", "New"),
            ("approved", "Approved"),
            ("generating", "Generating"),
            ("generated", "Generated"),
            ("printing", "Printing"),
            ("printed", "Printed"),
            ("distributed", "Distributed"),
        ],
        default="new",
    )

    id_pdf = fields.Binary("ID PASS")
    id_pdf_filename = fields.Char("ID File Name")
    merge_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("merged", "Merged"),
            ("error_sending", "Error Sending"),
            ("error_merging", "Error Merging"),
        ],
        default="draft",
    )
    approved_by = fields.Many2one("res.users")
    printed_by = fields.Many2one("res.users")
    distributed_by = fields.Many2one("res.users")
    date_approved = fields.Date()
    date_printed = fields.Date()
    date_distributed = fields.Date()
    date_merged = fields.Date()

    def refresh_data(self):
        return

    def approve_batch(self):
        """
        These are used to approve or validate a batch
        """
        for rec in self:
            rec.date_approved = date.today()
            rec.approved_by = self.env.user.id
            rec.status = "approved"
            message = _("{} validated this batch on {}.").format(
                rec.approved_by.name, datetime.now().strftime("%B %d, %Y at %H:%M")
            )
            rec.save_to_mail_thread(message)

    def generate_batch(self):
        return self._generate_batch(self)

    def _generate_batch(self, batch_ids):
        """
        These are used to generate cards from batch by
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
                    jobs.append(rec.delayable()._generate_cards(queued_ids))
                    queued_ids = []

            main_job = group(*jobs)
            main_job.on_done(self.delayable().mark_as_done(rec))
            main_job.delay()

            message_1 = _("{} started to generate this batch on {}.").format(
                self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
            )
            rec.save_to_mail_thread(message_1)

        message = _(
            f"{ctr_batch or ''} Batch(es) with total of {ctr_ids or ''} IDs are being generated."
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

    def _generate_cards(self, queue_ids):
        """
        These are used generate each cards from the Batch via Queue Jobs
        :param queued_ids: The Queue IDS.
        :return: Call generate_cards
        """
        queued_ids = self.env["spp.print.queue.id"].search([("id", "in", queue_ids)])
        queued_ids.generate_cards()

    def mark_as_done(self, rec):
        """
        These are used to set the batch as 'generated' when the
        Queue Job is Done
        :param rec: The Record.
        :return: Set status, call save_to_mail_thread then pass the api parameter
        """
        if not rec.queued_ids.filtered(lambda x: x.status != "generated"):
            rec.status = "generated"
            message = _("{} generated this batch on {}.").format(
                self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
            )
            rec.save_to_mail_thread(message)
            rec.pass_api_param()
        else:
            raise ValidationError(_("Some IDs are not generated"))

    def retry_pass_api(self):
        for rec in self:
            rec.pass_api_param()

    def pass_api_param(self):
        """
        These are used to pass the Batch ID on API
        to merge all Individual IDS to one PDF
        """
        for rec in self:
            batch_param = self.env["spp.id.pass"].search(
                [("id", "=", self.env.ref("spp_idqueue.id_template_batch_print").id)]
            )
            if batch_param and batch_param.auth_token and batch_param.api_url:
                token = _("Token %s", batch_param.auth_token)
                data = {
                    "batch_id": str(rec.id),
                }
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": token,
                }

                response = requests.post(
                    batch_param.api_url,
                    data=json.dumps(data),
                    headers=headers,
                )

                if response.status_code == 200:
                    rec.merge_status = "sent"
                else:
                    rec.merge_status = "error_sending"
            else:
                message = _("No Auth Token or API URL")
                raise ValidationError(message)
        return

    def print_batch(self):
        """
        These are used to set the Batch to 'printing'
        """
        for rec in self:
            rec.status = "printing"
            message = _("{} started to print this batch on {}.").format(
                self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
            )
            rec.save_to_mail_thread(message)
            for queue_id in rec.queued_ids:
                message = _("{} started to print this request on {}.").format(
                    self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
                )
                queue_id.save_to_mail_thread(message)

    def batch_printed(self):
        """
        These are used to set the Batch and each individual IDs
        to 'printed'
        """
        for rec in self:
            rec.date_printed = date.today()
            rec.printed_by = self.env.user.id
            rec.status = "printed"

            for queue_id in rec.queued_ids:
                queue_id.date_printed = date.today()
                queue_id.printed_by = self.env.user.id
                queue_id.status = "printed"
                message = _("{} printed this request on {}.").format(
                    self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
                )
                queue_id.save_to_mail_thread(message)

            message = _("{} printed this batch on {}").format(
                self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
            )
            rec.save_to_mail_thread(message)

    def batch_distributed(self):
        """
        These are used to set the Batch and each individual IDs
        to 'distributed'
        """
        for rec in self:
            rec.date_distributed = date.today()
            rec.distributed_by = self.env.user.id
            rec.status = "distributed"

            for queue_id in rec.queued_ids:
                queue_id.date_distributed = date.today()
                queue_id.status = "distributed"
                message = _("{} distributed this request on {}.").format(
                    self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
                )
                queue_id.save_to_mail_thread(message)

            message = _("{} distributed this batch on {}.").format(
                self.env.user.name, datetime.now().strftime("%B %d, %Y at %H:%M")
            )
            rec.save_to_mail_thread(message)

    def multi_approve_batch(self):
        """
        These are used for server action to approve multi-selected batches
        """
        if self.env.context.get("active_ids"):
            batch_ids = self.env["spp.print.queue.batch"].search(
                [
                    ("id", "in", self.env.context.get("active_ids")),
                    ("status", "=", "new"),
                ]
            )
            if batch_ids:
                max_rec = len(batch_ids)
                for batch_id in batch_ids:
                    batch_id.date_approved = date.today()
                    batch_id.approved_by = self.env.user.id
                    batch_id.status = "approved"
                    message = _("{} validated this batch on {}").format(
                        self.env.user.name,
                        datetime.now().strftime("%B %d, %Y at %H:%M"),
                    )
                    batch_id.save_to_mail_thread(message)

                message = _("%s batch(es) are validated.", max_rec)
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

    def multi_generate_batch(self):
        """
        These are used for server action to generate multi-selected batches
        """
        if self.env.context.get("active_ids"):
            batch_ids = self.env["spp.print.queue.batch"].search(
                [
                    ("id", "in", self.env.context.get("active_ids")),
                    ("status", "=", "approved"),
                ]
            )
            if batch_ids:
                return self._generate_batch(batch_ids)

    def multi_print_batch(self):
        """
        These are used for server action to print multi-selected batches
        """
        if self.env.context.get("active_ids"):
            batch_ids = self.env["spp.print.queue.batch"].search(
                [
                    ("id", "in", self.env.context.get("active_ids")),
                    ("status", "=", "generated"),
                    ("merge_status", "=", "merged"),
                ]
            )
            if batch_ids:
                max_rec = len(batch_ids)
                for batch_id in batch_ids:
                    batch_id.status = "printing"
                    message = _("{} started to print this batch on {}.").format(
                        self.env.user.name,
                        datetime.now().strftime("%B %d, %Y at %H:%M"),
                    )
                    batch_id.save_to_mail_thread(message)
                    for queue_id in batch_id.queued_ids:
                        message = _("{} started to print this request on {}.").format(
                            self.env.user.name,
                            datetime.now().strftime("%B %d, %Y at %H:%M"),
                        )
                        queue_id.save_to_mail_thread(message)

                message = _("%s batch(es) are being printed.", max_rec)
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

    def multi_printed_batch(self):
        """
        These are used for server action to set multi-selected batches and
        their Individual IDs as printed
        """
        if self.env.context.get("active_ids"):
            batch_ids = self.env["spp.print.queue.batch"].search(
                [
                    ("id", "in", self.env.context.get("active_ids")),
                    ("status", "=", "printing"),
                ]
            )
            if batch_ids:
                max_rec = len(batch_ids)
                for batch_id in batch_ids:
                    batch_id.date_printed = date.today()
                    batch_id.printed_by = self.env.user.id
                    batch_id.status = "printed"
                    message = _("{} printed this batch on {}.").format(
                        self.env.user.name,
                        datetime.now().strftime("%B %d, %Y at %H:%M"),
                    )
                    batch_id.save_to_mail_thread(message)

                    for queue_id in batch_id.queued_ids:
                        queue_id.date_printed = date.today()
                        queue_id.printed_by = self.env.user.id
                        queue_id.status = "printed"
                        message = _("{} printed this request on {}.").format(
                            self.env.user.name,
                            datetime.now().strftime("%B %d, %Y at %H:%M"),
                        )
                        queue_id.save_to_mail_thread(message)

                message = _("%s batch(es) are printed.", max_rec)
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

    def multi_distribute_batch(self):
        """
        These are used for server action to set multi-selected batches and
        their Individual IDs as distributed
        """
        if self.env.context.get("active_ids"):
            batch_ids = self.env["spp.print.queue.batch"].search(
                [
                    ("id", "in", self.env.context.get("active_ids")),
                    ("status", "=", "printed"),
                ]
            )
            if batch_ids:
                max_rec = len(batch_ids)
                for batch_id in batch_ids:
                    batch_id.date_distributed = date.today()
                    batch_id.distributed_by = self.env.user.id
                    batch_id.status = "distributed"
                    message = _("{} distributed this batch on {}.").format(
                        self.env.user.name,
                        datetime.now().strftime("%B %d, %Y at %H:%M"),
                    )
                    batch_id.save_to_mail_thread(message)

                    for queue_id in batch_id.queued_ids:
                        queue_id.date_distributed = date.today()
                        queue_id.status = "distributed"
                        message = _("{} distributed this request on {}.").format(
                            self.env.user.name,
                            datetime.now().strftime("%B %d, %Y at %H:%M"),
                        )
                        queue_id.save_to_mail_thread(message)

                message = _("%s batch(es) are distributed.", max_rec)
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

    def save_to_mail_thread(self, message):
        for rec in self:
            rec.message_post(body=message)
