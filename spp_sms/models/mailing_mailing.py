# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


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
        "spp.mailing.registrants", "mailing_individual_id", string="Individual"
    )
    mailing_registrant_group_ids = fields.One2many("spp.mailing.registrants", "mailing_group_id", string="Groups")
    mailing_program_ids = fields.One2many("spp.mailing.registrants", "mailing_program_id", string="Programs")
    mailing_cycle_ids = fields.One2many("spp.mailing.registrants", "mailing_cycle_id", string="Cycle")

    @api.onchange("mailing_registrant_individual_ids")
    def _individual_ids_onchange(self):
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Individual":
            vals = []
            m_domain = ""
            for rec in self.mailing_registrant_individual_ids:
                vals.append(rec.registrant_id.id)
            vals = list(dict.fromkeys(vals))
            m_domain = "[('id', 'in', " + str(vals) + ")]"
            self.mailing_domain = m_domain
            # main_vals = {vals}
            _logger.info("SMS Get Recipients: %s" % m_domain)

        return

    @api.onchange("mailing_registrant_group_ids")
    def _group_ids_onchange(self):
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Group":
            vals = []
            m_domain = ""
            for rec in self.mailing_registrant_group_ids:
                for rec_line in rec.registrant_id.group_membership_ids:
                    vals.append(rec_line.individual.id)
            vals = list(dict.fromkeys(vals))
            m_domain = "[('id', 'in', " + str(vals) + ")]"
            self.mailing_domain = m_domain
            # main_vals = {vals}
            _logger.info("SMS Get Recipients: %s" % m_domain)

        return

    @api.onchange("mailing_registrant_type")
    def _registrant_type_onchange(self):  # noqa: C901
        self.mailing_domain = ""
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Group":
            if self.mailing_registrant_group_ids:
                vals = []
                m_domain = ""
                for rec in self.mailing_registrant_group_ids:
                    for rec_line in rec.registrant_id.group_membership_ids:
                        vals.append(rec_line.individual.id)

                vals = list(dict.fromkeys(vals))
                m_domain = "[('id', 'in', " + str(vals) + ")]"
                self.mailing_domain = m_domain
                # main_vals = {vals}
                _logger.info("SMS Get Recipients: %s" % m_domain)
        elif self.mailing_type == "sms" and self.mailing_registrant_type == "Individual":
            if self.mailing_registrant_individual_ids:
                vals = []
                m_domain = ""
                for rec in self.mailing_registrant_individual_ids:
                    vals.append(rec.registrant_id.id)

                vals = list(dict.fromkeys(vals))
                m_domain = "[('id', 'in', " + str(vals) + ")]"
                self.mailing_domain = m_domain
                # main_vals = {vals}
                _logger.info("SMS Get Recipients: %s" % m_domain)
        elif self.mailing_type == "sms" and self.mailing_registrant_type == "Program":
            if self.mailing_program_ids:
                vals = []
                m_domain = ""
                for rec in self.mailing_program_ids:
                    for rec_line in rec.program_id.program_membership_ids:
                        if rec_line.state == "enrolled":
                            if rec_line.partner_id.is_group:
                                for rec_member in rec_line.partner_id.group_membership_ids:
                                    vals.append(rec_member.individual.id)
                            else:
                                vals.append(rec_line.partner_id.id)

                vals = list(dict.fromkeys(vals))
                m_domain = "[('id', 'in', " + str(vals) + ")]"
                self.mailing_domain = m_domain
                # main_vals = {vals}
                _logger.info("SMS Get Recipients: %s" % m_domain)
        elif self.mailing_type == "sms" and self.mailing_registrant_type == "Cycle":
            if self.mailing_cycle_ids:
                vals = []
                m_domain = ""
                for rec in self.mailing_cycle_ids:
                    for rec_line in rec.cycle_id.cycle_membership_ids:
                        if rec_line.state == "enrolled":
                            if rec_line.partner_id.is_group:
                                for rec_member in rec_line.partner_id.group_membership_ids:
                                    vals.append(rec_member.individual.id)
                            else:
                                vals.append(rec_line.partner_id.id)

                vals = list(dict.fromkeys(vals))
                m_domain = "[('id', 'in', " + str(vals) + ")]"
                self.mailing_domain = m_domain
                # main_vals = {vals}
                _logger.info("SMS Get Recipients: %s" % m_domain)

        return

    @api.onchange("mailing_program_ids")
    def _program_ids_onchange(self):
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Program":
            vals = []
            m_domain = ""
            for rec in self.mailing_program_ids:
                for rec_line in rec.program_id.program_membership_ids:
                    if rec_line.state == "enrolled":
                        if rec_line.partner_id.is_group:
                            for rec_member in rec_line.partner_id.group_membership_ids:
                                vals.append(rec_member.individual.id)
                        else:
                            vals.append(rec_line.partner_id.id)

            vals = list(dict.fromkeys(vals))
            m_domain = "[('id', 'in', " + str(vals) + ")]"
            self.mailing_domain = m_domain
            # main_vals = {vals}
            _logger.info("SMS Get Recipients: %s" % m_domain)

        return

    @api.onchange("mailing_cycle_ids")
    def _cycle_ids_onchange(self):
        if self.mailing_type == "sms" and self.mailing_registrant_type == "Cycle":
            vals = []
            m_domain = ""
            for rec in self.mailing_cycle_ids:
                for rec_line in rec.cycle_id.cycle_membership_ids:
                    if rec_line.state == "enrolled":
                        if rec_line.partner_id.is_group:
                            for rec_member in rec_line.partner_id.group_membership_ids:
                                vals.append(rec_member.individual.id)
                        else:
                            vals.append(rec_line.partner_id.id)

            vals = list(dict.fromkeys(vals))
            m_domain = "[('id', 'in', " + str(vals) + ")]"
            self.mailing_domain = m_domain
            # main_vals = {vals}
            _logger.info("SMS Get Recipients: %s" % m_domain)

        return
