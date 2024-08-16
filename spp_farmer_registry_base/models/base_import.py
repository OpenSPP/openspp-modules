import logging

from odoo import _, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPBaseImport(models.TransientModel):
    _inherit = "base_import.import"

    def execute_import(self, fields, columns, options, dryrun=False):
        if self.res_model == "res.partner":
            if "is_group" in fields and not ("farmer_given_name" in fields and "farmer_family_name" in fields):
                raise ValidationError(_("Farmer Given Name or Farmer Family Name is required"))
        return super().execute_import(fields, columns, options, dryrun=dryrun)
