# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import constants

_logger = logging.getLogger(__name__)


class CycleManager(models.Model):
    _name = "g2p.cycle.manager"
    _description = "Cycle Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.cycle.manager.default", "Default")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BaseCycleManager(models.AbstractModel):
    _name = "g2p.base.cycle.manager"
    _description = "Base Cycle Manager"

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    auto_approve_entitlements = fields.Boolean(
        string="Auto-approve Entitlements", default=False
    )

    def check_eligibility(self, cycle, beneficiaries=None):
        """
        Validate the eligibility of each beneficiary for the cycle
        """
        raise NotImplementedError()

    def prepare_entitlements(self, cycle):
        """
        Prepare the entitlements for the cycle
        """
        raise NotImplementedError()

    def validate_entitlements(self, cycle, cycle_memberships):
        """
        Validate the entitlements for the cycle
        """
        raise NotImplementedError()

    def new_cycle(self, name, new_start_date, sequence):
        """
        Create a new cycle for the program
        """
        raise NotImplementedError()

    def mark_distributed(self, cycle):
        """
        Mark the cycle as distributed
        """
        raise NotImplementedError()

    def mark_ended(self, cycle):
        """
        Mark the cycle as ended
        """
        raise NotImplementedError()

    def mark_cancelled(self, cycle):
        """
        Mark the cycle as cancelled
        """
        raise NotImplementedError()

    def add_beneficiaries(self, cycle, beneficiaries, state="draft"):
        """
        Add beneficiaries to the cycle
        """
        raise NotImplementedError()

    def on_start_date_change(self, cycle):
        """
        Hook for when the start date change
        """

    def on_state_change(self, cycle):
        """
        Hook for when the state change
        Args:
            cycle:

        Returns:

        """


class DefaultCycleManager(models.Model):
    _name = "g2p.cycle.manager.default"
    _inherit = ["g2p.base.cycle.manager", "g2p.manager.source.mixin"]
    _description = "Default Cycle Manager"

    cycle_duration = fields.Integer("Cycle Duration", default=30, required=True)
    approver_group_id = fields.Many2one(
        comodel_name="res.groups",
        string="Approver Group",
        copy=True,
    )

    def check_eligibility(self, cycle, beneficiaries=None):
        """
        :param cycle: The cycle that is being verified
        :type cycle: :class:`g2p_programs.models.cycle.G2PCycle`
        :param beneficiaries: the beneficiaries that need to be verified. By Default the one with the state ``draft``
                or ``enrolled`` are verified.
        :type beneficiaries: list or None

        :return: The list of eligible beneficiaries
        :rtype: list

        Validate the eligibility of each beneficiary for the cycle using the configured manager(s)
        :class:`g2p_programs.models.managers.eligibility_manager.BaseEligibilityManager`. If there is multiple managers
        for eligibility, each of them are run using the filtered list of eligible beneficiaries from the previous
        one.

        The ``state`` of beneficiaries is updated to either ``enrolled`` if they match the enrollment criteria
        or ``not_eligible`` in case they do not match them.


        """
        for rec in self:
            rec._ensure_can_edit_cycle(cycle)

            # Get all the enrolled beneficiaries
            if beneficiaries is None:
                beneficiaries = cycle.get_beneficiaries(["draft", "enrolled"])

            eligibility_managers = rec.program_id.get_managers(
                constants.MANAGER_ELIGIBILITY
            )
            filtered_beneficiaries = beneficiaries
            for manager in eligibility_managers:
                filtered_beneficiaries = manager.verify_cycle_eligibility(
                    cycle, filtered_beneficiaries
                )

            filtered_beneficiaries.write({"state": "enrolled"})

            beneficiaries_ids = beneficiaries.ids
            filtered_beneficiaries_ids = filtered_beneficiaries.ids
            _logger.info("Beneficiaries: %s", beneficiaries_ids)
            _logger.info("Filtered beneficiaries: %s", filtered_beneficiaries_ids)
            ids_to_remove = list(
                set(beneficiaries_ids) - set(filtered_beneficiaries_ids)
            )

            # Mark the beneficiaries as not eligible
            memberships_to_remove = self.env["g2p.cycle.membership"].browse(
                ids_to_remove
            )
            memberships_to_remove.write({"state": "not_eligible"})

            # Disable the entitlements of the beneficiaries
            entitlements = self.env["g2p.entitlement"].search(
                [
                    ("cycle_id", "=", cycle.id),
                    ("partner_id", "in", memberships_to_remove.mapped("partner_id.id")),
                ]
            )
            entitlements.write({"state": "cancelled"})

            return filtered_beneficiaries

    def prepare_entitlements(self, cycle):
        for rec in self:
            rec._ensure_can_edit_cycle(cycle)
            # Get all the enrolled beneficiaries
            beneficiaries = cycle.get_beneficiaries(["enrolled"])

            rec.program_id.get_manager(
                constants.MANAGER_ENTITLEMENT
            ).prepare_entitlements(cycle, beneficiaries)

    def mark_distributed(self, cycle):
        cycle.update({"state": constants.STATE_DISTRIBUTED})

    def mark_ended(self, cycle):
        cycle.update({"state": constants.STATE_ENDED})

    def mark_cancelled(self, cycle):
        cycle.update({"state": constants.STATE_CANCELLED})

    def validate_entitlements(self, cycle, cycle_memberships):
        # TODO: call the program's entitlement manager and validate the entitlements
        # TODO: Use a Job attached to the cycle
        # TODO: Implement validation workflow
        for rec in self:
            rec.program_id.get_manager(
                constants.MANAGER_ENTITLEMENT
            ).validate_entitlements(cycle_memberships)

    def new_cycle(self, name, new_start_date, sequence):
        _logger.info("Creating new cycle for program %s", self.program_id.name)
        _logger.info("New start date: %s", new_start_date)
        for rec in self:
            cycle = self.env["g2p.cycle"].create(
                {
                    "program_id": rec.program_id.id,
                    "name": name,
                    "state": "draft",
                    "sequence": sequence,
                    "start_date": new_start_date,
                    "end_date": new_start_date + timedelta(days=rec.cycle_duration),
                }
            )
            _logger.info("New cycle created: %s", cycle.name)
            return cycle

    def copy_beneficiaries_from_program(self, cycle, state="enrolled"):
        self._ensure_can_edit_cycle(cycle)

        for rec in self:
            beneficiary_ids = rec.program_id.get_beneficiaries(["enrolled"]).mapped(
                "partner_id.id"
            )
            rec.add_beneficiaries(cycle, beneficiary_ids, state)

    def add_beneficiaries(self, cycle, beneficiaries, state="draft"):
        """
        Add beneficiaries to the cycle
        """
        self._ensure_can_edit_cycle(cycle)
        _logger.info("Adding beneficiaries to the cycle %s", cycle.name)
        _logger.info("Beneficiaries: %s", beneficiaries)

        existing_ids = cycle.cycle_membership_ids.mapped("partner_id.id")
        new_beneficiaries = []
        for r in beneficiaries:
            if r not in existing_ids:
                new_beneficiaries.append(
                    [
                        0,
                        0,
                        {
                            "partner_id": r,
                            "enrollment_date": fields.Date.today(),
                            "state": state,
                        },
                    ]
                )
        if new_beneficiaries:
            cycle.update({"cycle_membership_ids": new_beneficiaries})
            return True
        else:
            return False

    def _ensure_can_edit_cycle(self, cycle):
        if cycle.state not in [cycle.STATE_DRAFT]:
            raise ValidationError(_("The Cycle is not in Draft Mode"))

    def on_state_change(self, cycle):
        if cycle.state == cycle.STATE_APPROVED:
            if not self.approver_group_id:
                raise ValidationError(_("The cycle approver group is not specified!"))
            else:
                if self.env.user.id not in self.approver_group_id.users.ids:
                    raise ValidationError(
                        _("You are not allowed to approve this cycle!")
                    )
