# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


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
            for queue in rec.queued_ids:
                queue.on_generate()
            if not rec.queued_ids.filtered(lambda x: x.status not in ["generated"]):
                rec.status = "generated"
                rec.pass_api_param()

    def pass_api_param(self):
        return

    def print_batch(self):
        for rec in self:
            rec.status = "printing"

    def batch_printed(self):
        for rec in self:
            rec.status = "printed"
