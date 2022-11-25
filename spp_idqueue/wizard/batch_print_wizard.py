# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
import math

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPBatchPrintWizard(models.TransientModel):
    _name = "spp.batch.print.wizard"
    _description = "Batch Print Wizard"

    @api.model
    def default_get(self, fields):
        res = super(OpenSPPBatchPrintWizard, self).default_get(fields)
        if self.env.context.get("active_ids"):
            queue_id = self.env["spp.print.queue.id"].search(
                [("id", "in", self.env.context.get("active_ids"))]
            )
            queue_ids = queue_id.filtered(
                lambda x: not x.batch_id and x.status == "approved"
            )
            if len(queue_ids) > 0:
                res["queue_ids"] = queue_ids
                res["id_count"] = len(queue_ids)
            else:
                raise UserError(_("There are no valid id requests!"))
            return res
        else:
            raise UserError(_("There are no selected id requests!"))

    name = fields.Char(string="Batch Name")
    id_count = fields.Integer(string="ID Count")
    max_id_per_batch = fields.Integer(string="Max ID per batch", default=1)
    batches_count = fields.Integer(
        string="Batches count to be printed", compute="_compute_batches_count"
    )
    queue_ids = fields.Many2many("spp.print.queue.id")

    def print_batch(self):
        for rec in self:
            id_count = 0
            batches_count = rec.batches_count
            batch_name = rec.name
            if batches_count > 1:
                batch_name = _("%s - 1", rec.name)
            batch_id = self.env["spp.print.queue.batch"].create({"name": batch_name})
            current_batch_count = 1
            for queue in rec.queue_ids:
                if not current_batch_count > batches_count:
                    id_count += 1
                    if not id_count > rec.max_id_per_batch:
                        queue.write({"batch_id": batch_id.id})
                    else:
                        if not current_batch_count == batches_count:
                            batch_name = f"{rec.name or ''} - {current_batch_count + 1}"
                            batch_id = self.env["spp.print.queue.batch"].create(
                                {"name": batch_name}
                            )
                            queue.write({"batch_id": batch_id.id})
                            id_count = 1

                        current_batch_count += 1

            return

    @api.depends("max_id_per_batch", "id_count")
    def _compute_batches_count(self):
        for rec in self:
            rec.batches_count = 1
            if rec.max_id_per_batch and rec.id_count:
                if rec.max_id_per_batch > rec.id_count:
                    rec.batches_count = 1
                else:
                    rec.batches_count = math.ceil(rec.id_count / rec.max_id_per_batch)

    def open_wizard(self):
        return {
            "name": "Batch Print",
            "view_mode": "form",
            "res_model": "spp.batch.print.wizard",
            "view_id": self.env.ref("spp_idqueue.batch_print_wizard_form_view").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.env.context,
        }
