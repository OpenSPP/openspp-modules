# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.sql import column_exists, create_column


class StockMove(models.Model):
    _inherit = "stock.move"
    entitlement_id = fields.Many2one("g2p.entitlement.inkind", "In-kind Entitlement", index=True)

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("entitlement_id")
        return distinct_fields

    def _get_source_document(self):
        res = super()._get_source_document()
        return self.entitlement_id.cycle_id or res

    def _assign_picking_post_process(self, new=False):
        super()._assign_picking_post_process(new=new)
        if new:
            picking_id = self.mapped("picking_id")
            entitlement_ids = self.mapped("entitlement_id.cycle_id")
            for entitlement_id in entitlement_ids:
                picking_id.message_post_with_source(
                    "mail.message_origin_link",
                    render_values={"self": picking_id, "origin": entitlement_id},
                    subtype_id=self.env.ref("mail.mt_note").id,
                )
        return


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    cycle_id = fields.Many2one("g2p.cycle", "Cycle")


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        fields = super()._get_custom_move_fields()
        fields += ["entitlement_id"]
        return fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cycle_id = fields.Many2one(related="group_id.cycle_id", string="Cycle", store=True, readonly=False)

    def _auto_init(self):
        """
        Create related field here, too slow
        when computing it afterwards through _compute_related.

        Since group_id.cycle_id is created in this module,
        no need for an UPDATE statement.
        """
        if not column_exists(self.env.cr, "stock_picking", "cycle_id"):
            create_column(self.env.cr, "stock_picking", "cycle_id", "int4")
        return super()._auto_init()
