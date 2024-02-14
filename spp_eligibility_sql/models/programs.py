# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CustomG2PProgram(models.Model):
    _inherit = "g2p.program"

    def create_program_sql_eligibility(self, name, sql_query, entitlement_kind, entitlement_vars):
        """
        Create a program based with SQL .
        :param name: String. Name of the program.
        :param sql_query: String. SQL query for the eligibility criteria.
        :param entitlement_kind: String. Can be one of ["default","cash","inkind","basket_entitlement"].
        :param entitlement_vars: Dictionary. Variables based on entitlement_kind.
        :return:
        """
        if name and sql_query and entitlement_vars:
            if entitlement_kind:
                # Set default currency from the user's current company
                currency_id = self.env.user.company_id.currency_id and self.env.user.company_id.currency_id.id or False

                vals = {
                    "name": name,
                    "sql_query": sql_query,
                    "target_type": "group",
                    "eligibility_kind": "sql_eligibility",
                    "currency_id": currency_id,
                    "entitlement_kind": entitlement_kind,
                    "auto_approve_entitlements": True,
                    "approver_group_id": self.env.ref("g2p_registry_base.group_g2p_admin").id,
                }
                vals.update(entitlement_vars)
                create_program_wizard = self.env["g2p.program.create.wizard"].create(vals)
                return create_program_wizard.create_program()
            else:
                raise UserError(_("The entitlement kind must be specified."))
        else:
            raise UserError(_("The program name, SQL query, and entitlement dictionary must be provided."))
