from odoo import fields, models


class SPPResCountry(models.Model):
    _inherit = "res.country"

    lat_min = fields.Float(string="Latitude Min")
    lat_max = fields.Float(string="Latitude Max")
    lon_min = fields.Float(string="Longitude Min")
    lon_max = fields.Float(string="Longitude Max")
    faker_locale = fields.Char(string="Faker Locale")
    faker_locale_available = fields.Boolean(string="Faker Locale Available")
