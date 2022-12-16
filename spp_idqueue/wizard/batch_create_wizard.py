# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
import math

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPBatchCreateWizard(models.TransientModel):
    _name = "spp.batch.create.wizard"
    _description = "Create Batch Wizard"

    @api.model
    def default_get(self, fields):
        res = super(OpenSPPBatchCreateWizard, self).default_get(fields)
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
                raise UserError(_("No approved id requests selected!"))
            return res
        else:
            raise UserError(_("There are no selected id requests!"))

    name = fields.Char(string="Batch Name")
    id_count = fields.Integer(string="ID Count")
    max_id_per_batch = fields.Integer(string="Max ID per batch", default=20)
    batches_count = fields.Integer(
        string="Batches to be created", compute="_compute_batches_count"
    )
    queue_ids = fields.Many2many("spp.print.queue.id")

    def create_batch(self):
        for rec in self:
            id_count = 0
            batches_count = rec.batches_count
            batch_name = rec.name
            if batches_count > 1:
                batch_name = _("%s - 1", rec.name)
            batch_id = self.env["spp.print.queue.batch"].create({"name": batch_name})
            current_batch_count = 1
            queue_ids = []
            for queue in rec.queue_ids:
                if not current_batch_count > batches_count:
                    id_count += 1
                    if not id_count > rec.max_id_per_batch:
                        queue_ids.append([4, queue.id])
                    else:
                        batch_id.write({"queued_ids": queue_ids})
                        queue_ids = []
                        if not current_batch_count == batches_count:
                            batch_name = f"{rec.name or ''} - {current_batch_count + 1}"
                            batch_id = self.env["spp.print.queue.batch"].create(
                                {"name": batch_name}
                            )
                            queue_ids.append([4, queue.id])
                            id_count = 1
                            current_batch_count += 1

            # Write the last batch
            if queue_ids:
                batch_id.write({"queued_ids": queue_ids})

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
            "name": "Create Batch Printing",
            "view_mode": "form",
            "res_model": "spp.batch.create.wizard",
            "view_id": self.env.ref("spp_idqueue.batch_create_wizard_form_view").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.env.context,
        }
