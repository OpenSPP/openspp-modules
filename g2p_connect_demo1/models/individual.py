# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PIndividual(models.Model):
    _inherit = "res.partner"

    z_cst_ind_cyclone_aug_2022_injured = fields.Boolean(
        "Injured during Cyclone Aug 2022"
    )
    z_cst_ind_disability_level = fields.Integer("Disability level")  # 0-100
    z_cst_ind_receive_government_benefits = fields.Boolean(
        "Receive government benefits"
    )
    z_cst_ind_cyclone_aug_2022_lost_livestock = fields.Boolean(
        "Lost significant livestock during Cyclone Aug 2022"
    )
    z_cst_ind_cyclone_aug_2022_lost_primary_source_income = fields.Boolean(
        "Lost primary source income during Cyclone Aug 2022"
    )
