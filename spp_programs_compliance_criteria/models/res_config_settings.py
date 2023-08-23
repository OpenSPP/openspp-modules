from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    beneficiaries_automated_filtering_mechanism = fields.Selection(
        selection=[
            ("0", "No Automated Filtering Mechanism"),
            ("1", "On Cycle Memberships Creating Event"),
            ("2", "On Entitlement Creating Event"),
        ],
        required=True,
        default="0",
        config_parameter="spp_programs_compliance_criteria.beneficiaries_automated_filtering_mechanism",
        help="Automated Filtering Beneficiaries Mechanism:\n"
        "0. No Automated Filtering Mechanism\n"
        "1. On Cycle Memberships Creating Event\n"
        "2. On Entitlement Creating Event\n",
    )
