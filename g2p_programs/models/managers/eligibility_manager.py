# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EligibilityManager(models.Model):
    _name = "g2p.eligibility.manager"
    _description = "Eligibility Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program_membership.manager.default", "Default Eligibility")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BaseEligibilityManager(models.AbstractModel):
    _name = "g2p.program_membership.manager"
    _inherit = "base.programs.manager"
    _description = "Base Eligibility"

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    def enroll_eligible_registrants(self, program_memberships):
        """
        This method is used to validate if a user match the criteria needed to be enrolled in a program.
        Args:
            program_membership:

        Returns:
            bool: True if the user match the criterias, False otherwise.
        """
        raise NotImplementedError()

    def verify_cycle_eligibility(self, cycle, program_memberships):
        """
        This method is used to validate if a beneficiary match the criteria needed to be enrolled in a cycle.
        Args:
            cycle:
            program_membership:

        Returns:
            bool: True if the cycle match the criterias, False otherwise.
        """
        raise NotImplementedError()

    def import_eligible_registrants(self):
        """
        This method is used to import the beneficiaries in a program.
        Returns:
        """
        raise NotImplementedError()


class DefaultEligibilityManager(models.Model):
    _name = "g2p.program_membership.manager.default"
    _inherit = ["g2p.program_membership.manager", "g2p.manager.source.mixin"]
    _description = "Simple Eligibility"

    # TODO: rename to allow_
    # support_individual = fields.Boolean(string="Support Individual", default=False)
    # support_group = fields.Boolean(string="Support Group", default=False)

    # TODO: cache the parsed domain
    eligibility_domain = fields.Text(string="Domain", default="[]")

    def _prepare_eligible_domain(self, membership):
        ids = membership.mapped("partner_id.id")
        domain = [("id", "in", ids)]
        # TODO: use the config of the program
        if self.program_id.target_type == "group":
            domain += [("is_group", "=", True)]
        if self.program_id.target_type == "individual":
            domain += [("is_group", "=", False)]
        domain += self._safe_eval(self.eligibility_domain)
        return domain

    def enroll_eligible_registrants(self, program_memberships):
        # TODO: check if the beneficiary still match the criterias
        _logger.info("-" * 100)
        _logger.info("Checking eligibility for %s", program_memberships)
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
        domain = self._prepare_eligible_domain(membership)
        _logger.info("Eligibility domain: %s", domain)
        beneficiaries = self.env["res.partner"].search(domain).ids
        _logger.info("Beneficiaries: %s", beneficiaries)
        return beneficiaries
