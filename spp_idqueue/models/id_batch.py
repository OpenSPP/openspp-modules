# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


import json

import requests

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class OpenSPPPrintBatch(models.Model):
    _name = "spp.print.queue.batch"
    _description = "ID print Batch"

    name = fields.Char("Batch name")

    #  We should only allow `approved` id to be added to a batch
    queued_ids = fields.One2many("spp.print.queue.id", "batch_id", string="Queued IDs")

    status = fields.Selection(
        [
            ("new", "New"),
            ("generated", "Generated"),
            ("printing", "Printing"),
            ("printed", "Printed"),
        ],
        default="new",
    )

    id_pdf = fields.Binary("ID PASS")
    id_pdf_filename = fields.Char("ID File Name")

    def generate_batch(self):
        for rec in self:
            rec.queued_ids.generate_cards()
            if not rec.queued_ids.filtered(lambda x: x.status not in ["generated"]):
                rec.status = "generated"
                rec.pass_api_param()

    def pass_api_param(self):
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

                if not response.status_code == 200:
                    message = _(
                        f"ID Pass Error: {response.reason or ''} with Code: {response.status_code or ''}"
                        f"with Data: {response.data or ''}"
                    )
                    raise ValidationError(message)
            else:
                message = _("No Auth Token or API URL")
                raise ValidationError(message)
        return

    def print_batch(self):
        for rec in self:
            rec.status = "printing"

    def batch_printed(self):
        for rec in self:
            rec.status = "printed"
