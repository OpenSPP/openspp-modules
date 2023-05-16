import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IdDetailsIndividual(models.Model):
    _inherit = "res.partner"

    id_document_details = fields.Text(required=False)

    def scan_id_document_details_vals(self, details):
        name = ""
        if details.get("family_name"):
            name += f"{details['family_name']}, "
        if details.get("given_name"):
            name += f"{details['given_name']} "
        if self.addl_name:
            name += f"{self.addl_name} "

        vals = {
            "family_name": details.get("family_name"),
            "given_name": details.get("given_name"),
            "name": name,
            "birthdate": details.get("birth_date"),
            "gender": details.get("gender"),
            "id_document_details": "",
            "birth_place": details.get("birth_place_city", None),
        }
        return vals

    @api.onchange("id_document_details")
    def on_scan_id_document_details(self):
        try:
            if self.id_document_details:
                details = json.loads(self.id_document_details)
                if details:
                    vals = self.scan_id_document_details_vals(details)
                    if details.get("image"):
                        vals.update({"image_1920": details["image"]})

                    self.update(vals)
        except Exception as e:
            _logger.error(e)

        self.update(
            {
                "id_document_details": "",
            }
        )
