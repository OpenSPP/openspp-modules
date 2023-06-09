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

    def _prepare_eligible_domain(self, membership=None, beneficiaries=None):
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
        # domain += self._safe_eval(self.eligibility_domain)
        # _logger.debug("DOMAIN: %s" % domain)
        return domain

    def _get_beneficiaries_sql_query(self):
        res = []
        try:
            self._cr.execute(self.sql_query)
            beneficiaries = self._cr.dictfetchall()
        except Exception as e:
            raise UserError(_("Database Query Error: %s") % e) from e
        else:
            # Convert List Dict to List
            for b in beneficiaries:
                if b.get("id"):
                    res.append(b["id"])
                else:
                    raise UserError(_("The SQL Query must return the record ID field."))
        return res

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
            return self.env["g2p.cycle.membership"].search(
                [("partner_id", "in", beneficiaries)]
            )

    def _verify_eligibility(self, membership):
        domain = self._prepare_eligible_domain(membership=membership)
        _logger.debug("Eligibility domain: %s", domain)
        beneficiaries = self.env["res.partner"].search(domain).ids
        _logger.debug("Beneficiaries: %s", beneficiaries)
        return beneficiaries

    def import_eligible_registrants(self, state="draft"):
        for rec in self:
            beneficiaries = rec._get_beneficiaries_sql_query()
            domain = rec._prepare_eligible_domain(beneficiaries=beneficiaries)
            new_beneficiaries = self.env["res.partner"].search(domain)
            # logging.debug("Found %s beneficiaries", len(new_beneficiaries))

            # Exclude already added beneficiaries
            beneficiary_ids = rec.program_id.get_beneficiaries().mapped("partner_id")

            # logging.debug("Excluding %s beneficiaries", len(beneficiary_ids))
            new_beneficiaries = new_beneficiaries - beneficiary_ids
            # logging.debug("Finally %s beneficiaries", len(new_beneficiaries))

            if len(new_beneficiaries) < 1000:
                rec._import_registrants(new_beneficiaries, state=state, do_count=True)
            else:
                rec._import_registrants_async(new_beneficiaries, state=state)

    def _import_registrants_async(self, new_beneficiaries, state="draft"):
        self.ensure_one()
        program = self.program_id
        program.message_post(
            body="Import of %s beneficiaries started." % len(new_beneficiaries)
        )
        program.write({"locked": True, "locked_reason": "Importing beneficiaries"})

        jobs = []
        for i in range(0, len(new_beneficiaries), 10000):
            jobs.append(
                self.delayable()._import_registrants(
                    new_beneficiaries[i : i + 10000], state
                )
            )
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
        logging.info("Importing %s beneficiaries", len(new_beneficiaries))
        logging.info("updated")
        beneficiaries_val = []
        for beneficiary in new_beneficiaries:
            beneficiaries_val.append(
                (0, 0, {"partner_id": beneficiary.id, "state": state})
            )
        self.program_id.update({"program_membership_ids": beneficiaries_val})

        if do_count:
            # Compute Statistics
            self.program_id._compute_eligible_beneficiary_count()
            self.program_id._compute_beneficiary_count()
