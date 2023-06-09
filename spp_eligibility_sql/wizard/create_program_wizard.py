# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    # SQL-base Eligibility Manager
    eligibility_kind = fields.Selection(
        selection_add=[("sql_eligibility", "SQL-base Eligibility")]
    )
    sql_query = fields.Text(string="SQL Query")

    def _check_required_fields(self):
        res = super()._check_required_fields()
        if self.eligibility_kind == "sql_eligibility":
            if not self.sql_query:
                raise UserError(
                    _("A SQL Query is needed for this eligibility criteria type.")
                )

        if self.entitlement_kind == "basket_entitlement":
            if not self.entitlement_basket_id:
                raise UserError(
                    _(
                        "The Food Basket in Cycle Manager is required in the Basket entitlement manager."
                    )
                )
            if not self.basket_product_ids:
                raise UserError(
                    _("Items are required in the Basket entitlement manager.")
                )
            if self.manage_inventory and not self.warehouse_id:
                raise UserError(
                    _(
                        "For inventory management, the warehouse is required in the basket entitlement manager."
                    )
                )
        return res

    def _get_eligibility_manager(self, program_id):
        res = super()._get_eligibility_manager(program_id)
        if self.eligibility_kind == "sql_eligibility":
            # Add a new record to sql-base eligibility manager model
            def_mgr_obj = "g2p.program_membership.manager.sql"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "SQL Query",
                    "program_id": program_id,
                    "sql_query": self.sql_query,
                }
            )
            # Add a new record to eligibility manager parent model
            man_obj = self.env["g2p.eligibility.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": "%s,%s" % (def_mgr_obj, str(def_mgr.id)),
                }
            )
            res = {"eligibility_managers": [(4, mgr.id)]}
        return res
