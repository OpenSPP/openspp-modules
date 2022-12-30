# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPIssueIDPassWizard(models.TransientModel):
    _name = "spp.issue.idpass.wizard"
    _description = "Issue ID Pass Wizard"

    idpass_id = fields.Many2one("spp.id.pass", "IDPass ID")
    registrant_id = fields.Many2one("res.partner", "Registrant ID")

    def issue_idpass(self):
        """
        This calls the send_idpass_parameters to
        generate the id for this registrant
        """
        if self.idpass_id:
            vals = {"idpass": self.idpass_id.id}
            self.registrant_id.send_idpass_parameters(vals)
        else:
            raise UserError(_("There are no selected Template!"))
