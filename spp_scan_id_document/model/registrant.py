import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

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

        gender = None

        if details.get("gender"):
            details_gender = details.get("gender")
            gender = self.env["gender.type"].search(
                ["|", ("code", "=", details_gender), ("value", "=", details_gender)], limit=1
            )

            # If still not found, log a warning and raise an error
            if not gender:
                message = _("Gender '%s' not found. Please create the gender first.") % details_gender
                raise UserError(message)

        document_type = None
        if details.get("document_type"):
            details_document_type = details.get("document_type")
            document_type = self.env["g2p.id.type"].search([("name", "=", details_document_type)], limit=1)
            if not document_type:
                message = (
                    _("Document type '%s' not found. Please create the document type first.") % details_document_type
                )
                raise UserError(message)

        document_number = details.get("document_number", None)
        document_expiry_date = details.get("expiry_date", None)

        vals = {
            "family_name": details.get("family_name"),
            "given_name": details.get("given_name"),
            "name": name,
            "birthdate": details.get("birth_date"),
            "gender": gender.id if gender else False,
            "id_document_details": "",
            "birth_place": details.get("birth_place_city", None),
        }
        if document_type:
            vals.update(
                {
                    "reg_ids": [
                        (
                            0,
                            0,
                            {
                                "id_type": document_type.id,
                                "value": document_number,
                                "expiry_date": document_expiry_date,
                            },
                        )
                    ]
                }
            )

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
        except UserError:
            raise
        except Exception as e:
            _logger.error(e)

        self.update(
            {
                "id_document_details": "",
            }
        )
