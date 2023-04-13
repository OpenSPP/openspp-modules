# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()


class OpenSPPCreateMemberWizard(models.TransientModel):
    _name = "spp.create.member.wizard"
    _description = "Create Member Wizard"

    @api.model
    def default_get(self, fields):
        values = super().default_get(fields)
        parent = self.env["res.partner"]
        values['lang'] = values.get('lang') or parent.lang or self.env.lang
        return values

    group_id = fields.Many2one("res.partner", "Group")
    individual_id = fields.Many2one("res.partner", "Individual")
    role = fields.Many2many("g2p.group.membership.kind")
    state = fields.Selection(
        [("step1", "Select Role"), ("step2", "Fill-Out Form")],
        "Status",
        default="step1",
        readonly=True,
    )
    address = fields.Text()

    reg_ids = fields.One2many("g2p.reg.id", "partner_id", "Registrant IDs")
    is_registrant = fields.Boolean("Registrant", default=True)
    is_group = fields.Boolean("Group", default=False)

    name = fields.Char(index=True)

    related_1_ids = fields.One2many(
        "g2p.reg.rel", "destination", "Related to registrant 1"
    )
    related_2_ids = fields.One2many("g2p.reg.rel", "source", "Related to registrant 2")

    phone_number_ids = fields.One2many(
        "g2p.phone.number", "partner_id", "Phone Numbers"
    )

    registration_date = fields.Date()
    tags_ids = fields.Many2many("g2p.registrant.tags", string="Tags")

    family_name = fields.Char(translate=False)
    given_name = fields.Char(translate=False)
    addl_name = fields.Char("Additional Name", translate=False)
    birth_place = fields.Char()
    birthdate_not_exact = fields.Boolean("Approximate Birthdate")
    birthdate = fields.Date("Date of Birth")
    age = fields.Char(compute="_compute_calc_age", size=50, readonly=True)
    gender = fields.Selection(
        [("Female", "Female"), ("Male", "Male")],
    )
    lang = fields.Selection(_lang_get, string='Language')
    active_lang_count = fields.Integer(compute='_compute_active_lang_count')
    email = fields.Char()

    def create_member(self):
        for rec in self:
            individual_vals = {
                "family_name": rec.family_name,
                "given_name": rec.given_name,
                "addl_name": rec.addl_name or '',
                "name": rec.name,
                "is_registrant": rec.is_registrant,
                "is_group": rec.is_group,
                "registration_date": rec.registration_date or None,
                "lang": rec.lang or None,
                "address": rec.address or '',
                "email": rec.email or '',
                "birth_place": rec.birth_place or '',
                "birthdate_not_exact": rec.birthdate_not_exact,
                "birthdate": rec.birthdate or None,
                "gender": rec.gender or None,
            }
            member = self.env["res.partner"].create(individual_vals)
            member_vals = {
                "group": rec.group_id.id,
                "individual": member.id,
                "kind": rec.role or None
            }
            self.env["g2p.group.membership"].create(member_vals)
            message = _("{} has been created and added to {} as member.".format(member.name,
                                                                                rec.group_id.name))
            kind = "info"
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Create Member"),
                    "message": message,
                    "sticky": False,
                    "type": kind,
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }

    def next_step(self):
        if self.state == "step1":
            self.state = "step2"
        return self._reopen_self()

    def prev_step(self):
        if self.state == "step2":
            self.state = "step1"
        return self._reopen_self()

    def _reopen_self(self):
        return {
            "name": _("Create Member"),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    @api.depends('lang')
    def _compute_active_lang_count(self):
        lang_count = len(self.env['res.lang'].get_installed())
        for partner in self:
            partner.active_lang_count = lang_count

    @api.onchange("is_group", "family_name", "given_name", "addl_name")
    def name_change(self):
        for rec in self:
            name = ""
            if self.family_name:
                name += self.family_name + ", "
            if self.given_name:
                name += self.given_name + " "
            if self.addl_name:
                name += self.addl_name + " "
            rec.name = name

    @api.depends("birthdate")
    def _compute_calc_age(self):
        for line in self:
            line.age = self.compute_age_from_dates(line.birthdate)

    def compute_age_from_dates(self, partner_dob):
        now = datetime.strptime(str(fields.Datetime.now())[:10], "%Y-%m-%d")
        if partner_dob:
            dob = partner_dob
            delta = relativedelta(now, dob)
            # years_months_days = str(delta.years) +"y "+ str(delta.months) +"m "+ str(delta.days)+"d"
            years_months_days = str(delta.years)
        else:
            years_months_days = "No Birthdate!"
        return years_months_days
