import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ExtensionServices(models.Model):
    _name = "spp.farm.extension"
    _description = "Extension Services"

    farm_id = fields.Many2one("res.partner", string="Farm", required=True)
    land_id = fields.Many2one(
        "spp.land.record",
        string="Land",
        required=False,
        domain="[('farm_id', '=', farm_id)]",
    )

    extension_services_type = fields.Selection(
        [("training", "Training"), ("advisory", "Advisory")],
    )
    extension_services_provider = fields.Char()
    extension_services_date = fields.Date()
    extension_services_topic = fields.Char()
    # extension_services_duration = fields.Float(string='Extension Services Duration')
    # extension_services_cost = fields.Float(string='Extension Services Cost')
    # extension_services_remarks = fields.Text(string='Extension Services Remarks')

    @api.onchange("farm_id")
    def _onchange_farm_id(self):
        for rec in self:
            rec.land_id = False
