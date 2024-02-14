# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPHouseVisit(models.Model):
    _name = "spp.event.house.visit"
    _description = "House Visit"

    summary = fields.Char()
    is_farm = fields.Boolean(default=False)
    farm_size_acre = fields.Float()
    photo = fields.Binary()
    photo_filename = fields.Char()
    number_of_pigs = fields.Integer()
    number_of_cows = fields.Integer()
    no_food_stock = fields.Integer()
    disabled = fields.Boolean(default=False)

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
