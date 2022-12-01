import json

from odoo import api, fields, models


class IdDetailsIndividual(models.Model):
    _inherit = "res.partner"

    id_document_details = fields.Text(required=False)

    @api.onchange("id_document_details")
    def on_scan_id_document_details(self):
        try:
            if self.id_document_details:
                details = json.loads(self.id_document_details)
                name = ""
                if details["family_name"]:
                    name += f"{details['family_name']}, "
                if details["given_name"]:
                    name += f"{details['given_name']} "
                if self.addl_name:
                    name += f"{self.addl_name} "
                vals = {
                    "family_name": details["family_name"],
                    "given_name": details["given_name"],
                    "name": name,
                    "birthdate": details["birth_date"],
                    "gender": details["gender"],
                    "id_document_details": "",
                }
                self.update(vals)
        except json.decoder.JSONDecodeError:
            pass
