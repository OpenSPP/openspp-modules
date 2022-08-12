# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import models


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    def _compute_count_and_set(self, field_name, kinds, criteria):
        """
        This method is used to compute the count then set it.
        :param field_name: The Field Name.
        :param kinds: The Kinds.
        :param criteria: The Criterias.
        :return: The count then set it on the Field Name.
        """
        for record in self:
            if record["is_group"]:
                record[field_name] = record.count_individuals(
                    kinds=kinds, criteria=criteria
                )
            else:
                record[field_name] = None
