# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


# Extending the built-in res.partner model in Odoo to accommodate PMT specific fields
class G2PGroupPMT(models.Model):
    _inherit = "res.partner"

    # Boolean fields capturing specific conditions of an individual
    x_cst_indv_gce_ol = fields.Boolean("Lower than G.C.E. Ordinary Level")
    x_cst_indv_school_age = fields.Boolean("Currently not attending school or other educational institution")
    x_cst_indv_chronic_disease = fields.Boolean("Long-term (chronic) disease")
    x_cst_indv_disability = fields.Boolean("Disability")

    # Floating-point field to store the computed PMT score of the group
    z_ind_grp_pmt_score = fields.Float(
        "PMT Score of the group",
        compute="_compute_z_ind_grp_pmt_score",
        compute_sudo=True,
    )
    grp_pmt_score = fields.Float("PMT Score of group", compute="_compute_grp_pmt_score", store=True)
    area_calc = fields.Many2one("spp.area", compute="_compute_area")

    def _compute_area(self):
        for rec in self:
            area_calc = None
            if rec.is_group:
                if rec.group_membership_ids:
                    individual = rec.group_membership_ids.mapped("individual.id")
                    members = self.env["res.partner"].search([("id", "in", individual), ("area_id", "!=", False)])
                    if members:
                        area_calc = members[0].area_id.id

                if area_calc:
                    rec.area_id = area_calc

            rec.area_calc = area_calc

    def compute_score(self, field_name):
        hh_area = self.area_id

        model = self.env["ir.model"].search([("model", "=", "res.partner")])

        fields = self.env["ir.model.fields"].search(
            [
                ("model_id", "=", model.id),
                ("with_weight", "=", True),
                ("target_type", "=", "indv"),
            ]
        )
        weights = {}
        if fields:
            for field in fields:
                if hh_area:
                    areas = field.area_ids.filtered(lambda a: a.name.id == hh_area.id)
                    if areas:
                        weights.update({field.name: areas[0].weight})
                    else:
                        weights.update({field.name: field.field_weight})
                else:
                    weights.update({field.name: field.field_weight})

        for record in self:
            if weights:
                z_ind_grp_pmt_score = 0
                if record.group_membership_ids:
                    total_score = 0.0
                    total_weight = 0.0
                    # Iterating through each member of the group to calculate the PMT score
                    for ind in record.group_membership_ids:
                        for field, weight in weights.items():
                            if hasattr(ind.individual, field):
                                total_score += getattr(ind.individual, field) * weight
                                total_weight += weight
                    if total_weight > 0:
                        z_ind_grp_pmt_score = total_score / total_weight
                    else:
                        z_ind_grp_pmt_score = 0
                setattr(record, field_name, z_ind_grp_pmt_score)
            else:
                setattr(record, field_name, 0)

    def _compute_z_ind_grp_pmt_score(self):
        self.compute_score("z_ind_grp_pmt_score")

    def _compute_grp_pmt_score(self):
        self.compute_score("grp_pmt_score")
