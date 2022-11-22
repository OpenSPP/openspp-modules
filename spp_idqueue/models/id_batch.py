# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPPrintBatch(models.Model):
    _name = "spp.print.queue.batch"
    _description = "ID print Batch"

    name = fields.Char("Batch name")

    #  We should only allow `approved` id to be added to a batch
    queued_ids = fields.Many2one("spp.print.queue.id", string="Queued IDs")

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
