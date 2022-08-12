# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class Image(models.Model):
    _inherit = "base_multi_image.image"

    photo_category_id = fields.Many2one("spp.photo.category", "Photo Category")
    storage = fields.Selection(
        [
            ("db", "File"),
            ("url", "URL"),
            ("file", ""),
            ("filestore", ""),
        ],
        required=True,
        default="db",
    )

    storage_select = fields.Selection(
        [
            ("db", "File"),
            ("url", "URL"),
        ],
        required=True,
        default="db",
    )

    @api.onchange("storage_select")
    def _onchange_storage_select(self):
        """
        This method is used to write storage field based on storage_select.
        :param storage: The Storage.
        :return: storage
        """
        if self.storage_select:
            self.storage = self.storage_select
