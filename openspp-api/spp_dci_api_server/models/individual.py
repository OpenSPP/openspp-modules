from odoo import models


class SPPIndividualCustom(models.Model):
    _inherit = "res.partner"

    def get_dci_individual_registry_data(self):
        """
        The function `get_dci_individual_registry_data` retrieves individual registry data and returns
        it in a specific format.
        :return: a list of dictionaries, where each dictionary represents an individual's registry data.
        Each dictionary contains the following key-value pairs:
        """
        reg_records = []

        for rec in self:
            identifier = []
            for reg_id in rec.reg_ids:
                if reg_id.value and reg_id.id_type and reg_id.id_type.name:
                    identifier.append(
                        {
                            "name": reg_id.id_type.name,
                            "identifier": reg_id.value,
                        }
                    )
            if not identifier:
                continue

            reg_records.append(
                {
                    "identifier": identifier,
                    "birthDate": str(rec.birthdate),
                    "givenName": rec.given_name,
                    "familyName": rec.family_name,
                    "sex": rec.gender.lower() if rec.gender else "",
                    "birthPlace": rec.birth_place,
                }
            )
        return reg_records
