# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

SPP_MAILING_REGISTRANTS = "spp.mailing.registrants"


class Mailing(models.Model):
    _inherit = "mailing.mailing"

    mailing_registrant_type = fields.Selection(
        selection=[
            ("Group", "Group"),
            ("Individual", "Individual"),
            ("Program", "Program"),
            ("Cycle", "Cycle"),
        ],
        default="Group",
    )
    mailing_registrant_individual_ids = fields.One2many(
        SPP_MAILING_REGISTRANTS, "mailing_individual_id", string="Individual"
    )
    mailing_registrant_group_ids = fields.One2many(
        SPP_MAILING_REGISTRANTS, "mailing_group_id", string="Groups"
    )
    mailing_program_ids = fields.One2many(
        SPP_MAILING_REGISTRANTS, "mailing_program_id", string="Programs"
    )
    mailing_cycle_ids = fields.One2many(
        SPP_MAILING_REGISTRANTS, "mailing_cycle_id", string="Cycle"
    )

    def _update_mailing_domain(self, vals):
        """Update mailing domain and log the change.

        Args:
            vals: List of IDs to include in domain
        """

        if not vals:
            return

        vals = list(dict.fromkeys(vals))  # Remove duplicates
        m_domain = "[('id', 'in', " + str(vals) + ")]"
        self.mailing_domain = m_domain
        _logger.info("SMS Get Recipients: %s" % m_domain)

    @api.onchange("mailing_registrant_individual_ids")
    def _individual_ids_onchange(self):
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Individual":
            vals = []
            for rec in self.mailing_registrant_individual_ids:
                vals.append(rec.registrant_id.id)
            self._update_mailing_domain(vals)

    @api.onchange("mailing_registrant_group_ids")
    def _group_ids_onchange(self):
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Group":
            vals = []
            for rec in self.mailing_registrant_group_ids:
                for rec_line in rec.registrant_id.group_membership_ids:
                    vals.append(rec_line.individual.id)
            self._update_mailing_domain(vals)

    @api.onchange("mailing_registrant_type")
    def _registrant_type_onchange(self):  # noqa: C901
        if self.mailing_type != "sms":
            return

        self.mailing_domain = ""
        if self.mailing_registrant_type == "Group":
            vals = []
            for rec in self.mailing_registrant_group_ids:
                for rec_line in rec.registrant_id.group_membership_ids:
                    vals.append(rec_line.individual.id)
            self._update_mailing_domain(vals)
        elif self.mailing_registrant_type == "Individual":
            vals = []
            for rec in self.mailing_registrant_individual_ids:
                vals.append(rec.registrant_id.id)
            self._update_mailing_domain(vals)
        elif self.mailing_registrant_type == "Program":
            vals = []
            for rec in self.mailing_program_ids:
                vals = self._get_enrolled_members(
                    rec.program_id, "program_id", "program_membership_ids"
                )
            self._update_mailing_domain(vals)
        elif self.mailing_registrant_type == "Cycle":
            vals = self._get_enrolled_members(
                self.mailing_cycle_ids, "cycle_id", "cycle_membership_ids"
            )
            self._update_mailing_domain(vals)

    def _get_enrolled_members(self, records, record_field, membership_field):
        """Helper method to get enrolled members from program/cycle records.

        Args:
            records: Program/Cycle records to process
            record_field: Name of the field to access the main record (program_id/cycle_id)
            membership_field: Name of the membership field to access

        Returns:
            list: List of individual IDs
        """
        vals = []
        for rec in records:
            main_record = getattr(rec, record_field)
            for rec_line in getattr(main_record, membership_field):
                if rec_line.state == "enrolled":
                    if rec_line.partner_id.is_group:
                        vals.extend(
                            member.individual.id
                            for member in rec_line.partner_id.group_membership_ids
                        )
                    else:
                        vals.append(rec_line.partner_id.id)
        return vals

    @api.onchange("mailing_program_ids")
    def _program_ids_onchange(self):
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Program":
            vals = self._get_enrolled_members(
                self.mailing_program_ids, "program_id", "program_membership_ids"
            )
            self._update_mailing_domain(vals)

    @api.onchange("mailing_cycle_ids")
    def _cycle_ids_onchange(self):
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Cycle":
            vals = self._get_enrolled_members(
                self.mailing_cycle_ids, "cycle_id", "cycle_membership_ids"
            )
            self._update_mailing_domain(vals)
