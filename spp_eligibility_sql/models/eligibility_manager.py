# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class EligibilityManager(models.Model):
    _inherit = "g2p.eligibility.manager"

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program_membership.manager.sql", "SQL-based Eligibility")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class SQLEligibilityManager(models.Model):
    _name = "g2p.program_membership.manager.sql"
    _inherit = ["g2p.program_membership.manager", "g2p.manager.source.mixin"]
    _description = "SQL-based Eligibility"

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
    sql_query_valid_message = fields.Text("Query Validation Message")
    sql_record_count = fields.Integer("Record Count", default=0)

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

    def _prepare_eligible_domain(self, membership=None, beneficiaries=None):
        """
        Generate a domain based on the existing program membership.
        :param membership: recordset of program members
        :param beneficiaries: list of beneficiaries from the SQL query
        :return:
        """
        domain = []
        ids = None
        if membership is not None:
            ids = membership.mapped("partner_id.id")
        if beneficiaries is not None:
            ids = beneficiaries
        if ids:
            domain += [("id", "in", ids)]

        # Do not include disabled registrants
        domain += [("disabled", "=", False)]
        if self.program_id.target_type == "group":
            domain += [("is_group", "=", True)]
        if self.program_id.target_type == "individual":
            domain += [("is_group", "=", False)]
        return domain

    def _generate_sql_query(self):
        """
        Generate the SQL Query based on the user defined query.
        The SQL WHERE clause will be added to filter active, enabled, and either group or individual registrants.
        The user defined query will be added in the final where clause as a sub-query.
        :return: string sql_query
        """
        sql = self.sql_query
        # Remove DMLs in the query
        dmls = ["insert", "update", "delete"]
        for dml in dmls:
            if sql.upper().find(dml.upper()) >= 0:
                sql = "DML ERROR"
                _logger.info("SQL-based Eligibility: DML violation %s" % sql)
                break

        # Create a query to add the disabled and is_group fields in the where clause
        where_clause = "active AND disabled IS NULL"
        if self.program_id.target_type == "group":
            where_clause += " AND is_group"
        elif self.program_id.target_type == "individual":
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
        _logger.debug("DB Query: %s" % sql_query)

        return sql_query

    def _get_beneficiaries_sql_query(self):
        """
        Execute the SQL Query and store the record IDs to res
        :return: list res
        """
        if self.sql_query_valid == "valid":
            sql_query = self._generate_sql_query()
            res = []
            try:
                self._cr.execute(sql_query)  # pylint: disable=sql-injection
            except Exception as e:
                raise UserError(_("Database Query Error: %s") % e) from e
            else:
                beneficiaries = self._cr.dictfetchall()
                # Convert List Dict to List
                for b in beneficiaries:
                    res.append(b["id"])
            return res
        else:
            raise UserError(_("The SQL Query is not valid. Be sure to validate this in the Eligibility Manager."))

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
                # Add a parameter to comply with pre-commit sql-injection-error
                self._cr.execute(sql_query)  # pylint: disable=sql-injection
            except Exception as e:
                _logger.debug("Database Query Error: %s" % e)
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
                }
            )

    def enroll_eligible_registrants(self, program_memberships):
        _logger.debug("-" * 100)
        _logger.debug("Checking eligibility for %s", program_memberships)
        for rec in self:
            beneficiaries = rec._verify_eligibility(program_memberships)
            return self.env["g2p.program_membership"].search(
                [
                    ("partner_id", "in", beneficiaries),
                    ("program_id", "=", self.program_id.id),
                ]
            )

    def verify_cycle_eligibility(self, cycle, membership):
        for rec in self:
            beneficiaries = rec._verify_eligibility(membership)
            return self.env["g2p.cycle.membership"].search([("partner_id", "in", beneficiaries)])

    def _verify_eligibility(self, membership):
        domain = self._prepare_eligible_domain(membership=membership)
        _logger.debug("Eligibility domain: %s", domain)
        beneficiaries = self.env["res.partner"].search(domain).ids
        _logger.debug("Beneficiaries: %s", beneficiaries)
        return beneficiaries

    def import_eligible_registrants(self, state="draft"):
        ben_count = 0
        for rec in self:
            new_beneficiaries = rec._get_beneficiaries_sql_query()
            _logger.debug("Found %s beneficiaries", len(new_beneficiaries))

            # Exclude already added beneficiaries
            beneficiary_ids = rec.program_id.get_beneficiaries().mapped("partner_id.id")
            _logger.debug("Excluding %s beneficiaries", len(beneficiary_ids))

            new_beneficiaries = list(set(new_beneficiaries).difference(beneficiary_ids))
            _logger.debug("Finally %s beneficiaries", len(new_beneficiaries))

            ben_count = len(new_beneficiaries)
            if ben_count < 1000:
                rec._import_registrants(new_beneficiaries, state=state, do_count=True)
            else:
                rec._import_registrants_async(new_beneficiaries, state=state)

        return ben_count

    def _import_registrants_async(self, new_beneficiaries, state="draft"):
        self.ensure_one()
        program = self.program_id
        program.message_post(body="Import of %s beneficiaries started." % len(new_beneficiaries))
        program.write({"locked": True, "locked_reason": "Importing beneficiaries"})

        jobs = []
        for i in range(0, len(new_beneficiaries), 10000):
            jobs.append(self.delayable()._import_registrants(new_beneficiaries[i : i + 10000], state))
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_import_as_done())
        main_job.delay()

    def mark_import_as_done(self):
        self.ensure_one()
        self.program_id._compute_eligible_beneficiary_count()
        self.program_id._compute_beneficiary_count()

        self.program_id.locked = False
        self.program_id.locked_reason = None
        self.program_id.message_post(body=_("Import finished."))

    def _import_registrants(self, new_beneficiaries, state="draft", do_count=False):
        _logger.debug("Importing %s beneficiaries", len(new_beneficiaries))
        beneficiaries_val = []
        for beneficiary_id in new_beneficiaries:
            beneficiaries_val.append((0, 0, {"partner_id": beneficiary_id, "state": state}))
        self.program_id.update({"program_membership_ids": beneficiaries_val})

        if do_count:
            # Compute Statistics
            self.program_id._compute_eligible_beneficiary_count()
            self.program_id._compute_beneficiary_count()
