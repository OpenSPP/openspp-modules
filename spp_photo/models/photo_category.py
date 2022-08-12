# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class OpenSPPPhotoCategory(models.Model):
    _name = "spp.photo.category"
    _description = "Photo Category"

    name = fields.Char(string="Name")
