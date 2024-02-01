# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    # SQL-base Eligibility Manager
    eligibility_kind = fields.Selection(selection_add=[("sql_eligibility", "SQL-base Eligibility")])
    sql_query = fields.Text(string="SQL Query")
    sql_query_valid = fields.Selection(
        [
            ("new", "New"),
            ("valid", "Valid"),
            ("invalid", "Invalid"),
            ("recheck", "Needs Re-checking"),
        ],
        string="SQL Query Status",
        default="new",
    )
    sql_record_count = fields.Integer("Record Count", default=0)
    sql_query_valid_message = fields.Text("Query Validation Message")

    @api.onchange("sql_query")
    def _sql_query_onchange(self):
        """
        Changing the SQL Query should require the re-checking of the user defined query.
        Set the sql_query_valid field to 'recheck' and the sql_record_count to 0.
        :return:
        """
        for rec in self:
            rec.update(
                {
                    "sql_query_valid": "recheck",
                    "sql_record_count": 0,
                    "sql_query_valid_message": None,
                }
            )

    def _generate_sql_query(self, sql=""):
        """
        Generate the SQL Query based on the user defined query.
        The SQL WHERE clause will be added to filter active, enabled, and either group or individual registrants.
        The user defined query will be added in the final where clause as a sub-query.
        :return: string sql_query
        """
        if not sql:
            sql = self.sql_query
        # Remove DMLs in the query
        dmls = ["insert", "update", "delete"]
        for dml in dmls:
            if sql.upper().find(dml.upper()) >= 0:
                sql = "DML ERROR"
                _logger.info("SQL-based Eligibility Wizard: DML violation %s" % sql)
                break

        # Create a query to add the disabled and is_group fields in the where clause
        where_clause = "active AND disabled IS NULL"
        if self.target_type == "group":
            where_clause += " AND is_group"
        elif self.target_type == "individual":
            where_clause += " AND NOT is_group"

        sql_query = f"""
            WITH tbl AS (
                {sql}
            )
            SELECT id FROM res_partner
            WHERE
            {where_clause}
            AND id IN (
                SELECT id FROM tbl
            )
        """
        _logger.debug("SQL-based Eligibility Wizard: DB Query: %s" % sql_query)

        return sql_query

    def test_sql_query(self):
        """
        Check if the SQL Query is valid.
        If valid, it must return the res_partner id field and must contain at least 1 record.
        :return:
        """
        for rec in self:
            sql_query = rec._generate_sql_query()
            record_count = 0
            try:
                self._cr.execute(sql_query)  # pylint: disable=sql-injection
            except Exception as e:
                _logger.debug("SQL-based Eligibility Wizard: Database Query Error: %s" % e)
                sql_query_valid = "invalid"
                sql_query_valid_message = _("Database Query Error: %s") % e
                self._cr.rollback()
            else:
                beneficiaries = self._cr.dictfetchall()
                # Convert List Dict to List
                if beneficiaries:
                    if not beneficiaries[0].get("id"):
                        sql_query_valid = "invalid"
                        sql_query_valid_message = _("The SQL Query must return the record ID field.")
                    else:
                        record_count = len(beneficiaries)
                        sql_query_valid = "valid"
                        sql_query_valid_message = None
                else:
                    sql_query_valid = "valid"
                    sql_query_valid_message = _("The SQL Query is valid but it did not return any record.")
            rec.update(
                {
                    "sql_query_valid": sql_query_valid,
                    "sql_query_valid_message": sql_query_valid_message,
                    "sql_record_count": record_count,
                    "state": "step1",
                }
            )
            return self._reopen_self()

    def _check_required_fields(self):
        res = super()._check_required_fields()
        if self.eligibility_kind == "sql_eligibility":
            if not self.sql_query:
                raise UserError(_("A SQL Query is needed for this eligibility criteria type."))
            elif not self.sql_query_valid:
                raise UserError(_("The SQL Query must be validated first."))
            elif not self.sql_record_count:
                raise UserError(_("The SQL Query must return 1 or more record."))

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
                    "sql_query_valid": self.sql_query_valid,
                    "sql_query_valid_message": self.sql_query_valid_message,
                    "sql_record_count": self.sql_record_count,
                }
            )
            # Add a new record to eligibility manager parent model
            man_obj = self.env["g2p.eligibility.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": f"{def_mgr_obj},{str(def_mgr.id)}",
                }
            )
            res = {"eligibility_managers": [(4, mgr.id)]}
        return res
