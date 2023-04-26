# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


@api.model
def _lang_get(self):
    return self.env["res.lang"].get_installed()


class OpenSPPCreateMemberWizard(models.TransientModel):
    _name = "spp.create.member.wizard"
    _description = "Create Member Wizard"

    @api.model
    def default_get(self, fields):
        values = super().default_get(fields)
        parent = self.env["res.partner"]
        values["lang"] = values.get("lang") or parent.lang or self.env.lang
        return values

    group_id = fields.Many2one("res.partner", "Group")
    head_member = fields.Many2one("res.partner", compute="_compute_head_member")
    role = fields.Many2many("g2p.group.membership.kind")
    state = fields.Selection(
        [("step1", "Select Role"), ("step2", "Fill-Out Form")],
        "Status",
        default="step1",
        readonly=True,
    )
    address = fields.Text()

    reg_ids = fields.One2many(
        "spp.create.member.id", "create_member_id", "Registrant IDs"
    )
    is_registrant = fields.Boolean("Registrant", default=True)
    is_group = fields.Boolean("Group", default=False)

    name = fields.Char(index=True)
    phone_number_ids = fields.One2many(
        "spp.create.member.phone", "create_member_id", "Phone Numbers"
    )

    registration_date = fields.Date()

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
    lang = fields.Selection(_lang_get, string="Language")
    active_lang_count = fields.Integer(compute="_compute_active_lang_count")
    email = fields.Char()

    def create_member(self):
        for rec in self:
            individual_vals = {
                "family_name": rec.family_name,
                "given_name": rec.given_name,
                "addl_name": rec.addl_name or "",
                "name": rec.name,
                "is_registrant": True,
                "is_group": False,
                "registration_date": rec.registration_date or None,
                "lang": rec.lang or None,
                "address": rec.address or "",
                "email": rec.email or "",
                "birth_place": rec.birth_place or "",
                "birthdate_not_exact": rec.birthdate_not_exact,
                "birthdate": rec.birthdate or None,
                "gender": rec.gender or None,
            }
            member = self.env["res.partner"].create(individual_vals)
            if rec.phone_number_ids:
                rec.insert_phone_numbers(member)

            if rec.reg_ids:
                rec.insert_ids(member)

            rec.update_custom_fields(member)
            member_vals = {
                "group": rec.group_id.id,
                "individual": member.id,
                "kind": rec.role or None,
            }
            self.env["g2p.group.membership"].create(member_vals)
            message = _("{} has been created and added to {} as member.").format(
                member.name, rec.group_id.name
            )
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

    def insert_phone_numbers(self, member):
        for rec in self:
            vals = []
            for phone in rec.phone_number_ids:
                data = {
                    "partner_id": member.id,
                    "phone_no": phone.phone_no,
                    "country_id": phone.country_id.id,
                    "date_collected": phone.date_collected,
                }
                vals.append(Command.create(data))

            if vals:
                member.update({"phone_number_ids": vals})

    def insert_ids(self, member):
        for rec in self:
            vals = []
            for ids in rec.reg_ids:
                data = {
                    "partner_id": member.id,
                    "id_type": ids.id_type.id,
                    "value": ids.value,
                    "expiry_date": ids.expiry_date,
                }
                vals.append(Command.create(data))

            if vals:
                member.update({"reg_ids": vals})

    def update_custom_fields(self, member):
        wizard_model = self.env["ir.model"].search([("model", "=", self._name)])
        wizard_custom_fields = self.env["ir.model.fields"].search(
            [("model_id", "=", wizard_model.id), ("name", "like", "cst_indv")]
        )
        vals = {}
        for custom_field in wizard_custom_fields:
            vals[custom_field.name] = self[custom_field.name]

        member.write(vals)

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

    @api.depends("lang")
    def _compute_active_lang_count(self):
        lang_count = len(self.env["res.lang"].get_installed())
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

    @api.onchange("role")
    def role_change(self):
        for rec in self:
            for role in rec.role:
                role_id = str(role.id)
                role_id = int(re.search(r"\d+", role_id).group())
                _logger.info(role_id)
                if (
                    role_id
                    == self.env.ref(
                        "g2p_registry_membership.group_membership_kind_head"
                    ).id
                    and rec.head_member
                ):
                    raise UserError(_("Only one head is allowed for this HH"))

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

    @api.depends("group_id")
    def _compute_head_member(self):
        """
        This sets head member of the group if the group has a member (group_membership_ids)
        """
        for rec in self:
            head_member = None
            if rec.group_id.group_membership_ids:
                for members in rec.group_id.group_membership_ids:
                    for kinds in members.kind:
                        kind_id = str(kinds.id)
                        kind_str = ""
                        for m in kind_id:
                            if m.isdigit():
                                kind_str = kind_str + m
                        if (
                            int(kind_str)
                            == self.env.ref(
                                "g2p_registry_membership.group_membership_kind_head"
                            ).id
                        ):
                            # _logger.info("Head Member: %s " % members.individual.name)
                            head_member = members.individual.id
                            break
                    if head_member:
                        break
            rec.head_member = head_member

    def check_custom_fields(self):
        model = self.env["ir.model"].search([("model", "=", "res.partner")])
        fields_name = self.env["ir.model.fields"].search(
            [("model_id", "=", model.id), ("name", "like", "cst_indv")]
        )

        model_wizard = self.env["ir.model"].search([("model", "=", self._name)])
        for field in fields_name:
            field_exists = self.env["ir.model.fields"].search(
                [("model_id", "=", model_wizard.id), ("name", "=", field.name)]
            )

            vals = {
                "model_id": model_wizard.id,
                "name": field.name,
                "field_description": field.field_description,
                "ttype": field.ttype,
                "target_type": field.target_type,
                "field_category": field.field_category,
                "help": field.help,
            }

            if not field_exists:
                self.env["ir.model.fields"].create(vals)
            else:
                field_exists.write(vals)

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(OpenSPPCreateMemberWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

        self.check_custom_fields()

        if view_type == "form":
            doc = etree.XML(res["arch"])
            basic_info_page = doc.xpath("//page[@name='basic_info']")

            model_fields_id = self.env["ir.model.fields"].search(
                [("model_id", "=", self._name)],
                order="ttype, field_description",
            )

            if basic_info_page:
                is_group = False
                custom_page = etree.Element("page", {"string": "Additional Details"})
                indicators_page = etree.Element("page", {"string": "Indicators"})

                custom_div = etree.SubElement(
                    custom_page, "div", {"class": "row mt16 o_settings_container"}
                )
                indicators_div = etree.SubElement(
                    indicators_page, "div", {"class": "row mt16 o_settings_container"}
                )
                for rec in model_fields_id:
                    els = rec.name.split("_")
                    if len(els) >= 3 and (
                        els[2] == "grp"
                        and not is_group
                        or els[2] == "indv"
                        and is_group
                    ):
                        continue

                    if len(els) >= 2 and els[1] == "cst":
                        custom_div2 = etree.SubElement(
                            custom_div,
                            "div",
                            {"class": "col-12 col-lg-6 o_setting_box"},
                        )
                        custom_div_left = etree.SubElement(
                            custom_div2, "div", {"class": "o_setting_left_pane"}
                        )
                        custom_div_right = etree.SubElement(
                            custom_div2, "div", {"class": "o_setting_right_pane"}
                        )
                        if rec.ttype == "boolean":
                            etree.SubElement(
                                custom_div_left, "field", {"name": rec.name}
                            )
                            etree.SubElement(
                                custom_div_right, "label", {"for": rec.name}
                            )
                            if rec.help:
                                custom_div_right_help = etree.SubElement(
                                    custom_div_right, "div", {"class": "text-muted"}
                                )
                                span = etree.SubElement(custom_div_right_help, "span")
                                span.text = rec.help

                        else:
                            etree.SubElement(
                                custom_div_right, "label", {"for": rec.name}
                            )

                            if rec.help:
                                custom_div_right_help = etree.SubElement(
                                    custom_div_right, "div", {"class": "text-muted"}
                                )
                                span = etree.SubElement(custom_div_right_help, "span")
                                span.text = rec.help

                            custom_div_right_inner_div = etree.SubElement(
                                custom_div_right, "div", {"class": "text-muted"}
                            )
                            etree.SubElement(
                                custom_div_right_inner_div, "field", {"name": rec.name}
                            )

                    elif len(els) >= 2 and els[1] == "ind":
                        indicators_div2 = etree.SubElement(
                            indicators_div,
                            "div",
                            {"class": "col-12 col-lg-6 o_setting_box"},
                        )
                        indicators_div_left = etree.SubElement(
                            indicators_div2, "div", {"class": "o_setting_left_pane"}
                        )
                        indicators_div_right = etree.SubElement(
                            indicators_div2, "div", {"class": "o_setting_right_pane"}
                        )
                        if rec.ttype == "boolean":
                            new_field = etree.SubElement(
                                indicators_div_left,
                                "field",
                                {
                                    "name": rec.name,
                                    "readonly": "1",
                                    "class": "oe_read_only",
                                },
                            )
                            etree.SubElement(
                                indicators_div_right, "label", {"for": rec.name}
                            )
                            if rec.help:
                                indicators_div_right_help = etree.SubElement(
                                    indicators_div_right, "div", {"class": "text-muted"}
                                )
                                span = etree.SubElement(
                                    indicators_div_right_help, "span"
                                )
                                span.text = rec.help
                        else:
                            etree.SubElement(
                                indicators_div_right, "label", {"for": rec.name}
                            )
                            if rec.help:
                                indicators_div_right_help = etree.SubElement(
                                    indicators_div_right, "div", {"class": "text-muted"}
                                )
                                span = etree.SubElement(
                                    indicators_div_right_help, "span"
                                )
                                span.text = rec.help
                            indicators_div_right_inner_div = etree.SubElement(
                                indicators_div_right, "div", {"class": "text-muted"}
                            )
                            new_field = etree.SubElement(
                                indicators_div_right_inner_div,
                                "field",
                                {"name": rec.name},
                            )

                        new_field.set("readonly", "1")
                        modifiers = {"readonly": True}
                        new_field.set("modifiers", json.dumps(modifiers))

                if custom_div.getchildren():
                    basic_info_page[0].addnext(custom_page)
                if indicators_div.getchildren():
                    basic_info_page[0].addnext(indicators_page)

                res["arch"] = etree.tostring(doc, encoding="unicode")

        return res


class OpenSPPCreateMemberPhoneNumber(models.TransientModel):
    _name = "spp.create.member.phone"
    _description = "Create Member Phone Numbers"

    create_member_id = fields.Many2one("spp.create.member.wizard", required=True)
    phone_no = fields.Char("Phone Number", required=True)
    country_id = fields.Many2one("res.country", "Country")
    date_collected = fields.Date(default=fields.Date.today)


class OpenSPPCreateMemberIDs(models.TransientModel):
    _name = "spp.create.member.id"
    _description = "Create Member IDs"

    create_member_id = fields.Many2one("spp.create.member.wizard", required=True)
    id_type = fields.Many2one("g2p.id.type", "ID Type", required=True)
    value = fields.Char(size=100)
    expiry_date = fields.Date()
