import os

from odoo import api, fields, models
from odoo.tools.misc import file_path

# from odoo.modules.module import get_resource_path


class Thumbnail(models.AbstractModel):
    _name = "spp.dms.mixins.thumbnail"
    _inherit = "image.mixin"
    _description = "DMS thumbnail and icon mixin"

    icon_url = fields.Char(string="Icon URL", compute="_compute_icon_url")

    def _get_icon_disk_path(self):
        """Obtain local disk path to record icon."""
        name = self._get_icon_placeholder_name()
        path = file_path(f"spp_dms/static/icons/{name}")
        return path or file_path("spp_dms/static/icons/file_unknown.svg")

    def _get_icon_placeholder_name(self):
        return "folder.svg"

    def _get_icon_url(self):
        """Obtain URL to record icon."""
        local_path = self._get_icon_disk_path()
        icon_name = os.path.basename(local_path)
        return "/spp_dms/static/icons/%s" % icon_name

    @api.depends("image_128")
    def _compute_icon_url(self):
        """Get icon static file URL."""
        for one in self:
            # Get URL to thumbnail or to the default icon by file extension
            one.icon_url = (
                f"/web/image/{one._name}/{one.id}/image_128/128x128?crop=1" if one.image_128 else one._get_icon_url()
            )
