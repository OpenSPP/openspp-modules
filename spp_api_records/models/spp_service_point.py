from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SppServicePoint(models.Model):
    _inherit = "spp.service.point"

    program_id = fields.Many2many(
        comodel_name="g2p.program",
        string="Program",
        compute="_compute_program_id",
        search="_search_program_id",
        store=False,
    )

    def _compute_program_id(self):
        SQL_QUERY = """
        SELECT
            gesprel.spp_service_point_id AS sp_id,
            gc.program_id AS prg_id
        FROM
            g2p_entitlement ge
            JOIN g2p_entitlement_spp_service_point_rel gesprel ON ge.id = gesprel.g2p_entitlement_id
            JOIN g2p_cycle gc ON ge.cycle_id = gc.id
        WHERE
            gesprel.spp_service_point_id IN %(self_ids)s

        UNION ALL

        SELECT
            geisprel.spp_service_point_id AS sp_id,
            gc.program_id AS prg_id
        FROM
            g2p_entitlement_inkind gei
            JOIN g2p_entitlement_inkind_spp_service_point_rel geisprel ON gei.id = geisprel.g2p_entitlement_inkind_id
            JOIN g2p_cycle gc ON gei.cycle_id = gc.id
        WHERE
            geisprel.spp_service_point_id IN %(self_ids)s
        """
        self.env.cr.execute(SQL_QUERY, {"self_ids": tuple(self.ids)})
        res = self.env.cr.dictfetchall()
        for rec in self:
            rec_program_ids = []
            for item in res:
                if item["sp_id"] != rec.id:
                    continue
                rec_program_ids.append(item["prg_id"])
            rec.program_id = [(6, 0, rec_program_ids)]

    def _search_program_id(self, operator, value):
        if operator != "=":
            raise ValidationError(_("Operator is not supported!"))
        SQL_QUERY = """
        SELECT
            gesprel.spp_service_point_id AS sp_id,
            gc.program_id AS prg_id
        FROM
            g2p_entitlement ge
            JOIN g2p_entitlement_spp_service_point_rel gesprel ON ge.id = gesprel.g2p_entitlement_id
            JOIN g2p_cycle gc ON ge.cycle_id = gc.id
        WHERE
            gc.program_id = %(program_id)s

        UNION ALL

        SELECT
            geisprel.spp_service_point_id AS sp_id,
            gc.program_id AS prg_id
        FROM
            g2p_entitlement_inkind gei
            JOIN g2p_entitlement_inkind_spp_service_point_rel geisprel ON gei.id = geisprel.g2p_entitlement_inkind_id
            JOIN g2p_cycle gc ON gei.cycle_id = gc.id
        WHERE
            gc.program_id = %(program_id)s
        """
        self.env.cr.execute(SQL_QUERY, {"program_id": value})
        res = self.env.cr.dictfetchall()
        service_point_ids = [item["sp_id"] for item in res]
        return [("id", "in", service_point_ids)]
