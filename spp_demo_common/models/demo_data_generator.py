# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
import random

from faker import Faker

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPDemoDataGenerator(models.Model):
    _name = "spp.demo.data.generator"
    _description = "SPP Demo Data Generator"

    def _default_number_of_groups(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.number_of_groups", 10))

    def _default_members_range_from(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.members_range_from", 1))

    def _default_members_range_to(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.members_range_to", 10))

    def _default_batch_size(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.batch_size", 100))

    def _default_locale_origin(self):
        company_lang = self.env.user.company_id.partner_id.lang
        if company_lang:
            lang = self.env["res.lang"].search([("code", "=", company_lang)], limit=1)
            if lang:
                return lang
        return self.env.ref("base.lang_en")

    def _default_queue_job_minimum_size(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.queue_job_minimum_size", 500))

    ID_TYPES_INDIVIDUAL = [
        "Passport",
        "National ID",
    ]

    ID_TYPES_GROUP = [
        "Business Permit",
        "Registration Certificate",
    ]

    GENDERS = [
        "Male",
        "Female",
    ]

    name = fields.Char(string="Name", required=True)
    remember_settings = fields.Boolean(string="Remember Settings", default=False)
    number_of_groups = fields.Integer(string="Number of Groups", default=_default_number_of_groups, required=True)
    members_range_from = fields.Integer(
        string="Members per Group (From)", default=_default_members_range_from, required=True
    )
    members_range_to = fields.Integer(string="Members per Group (To)", default=_default_members_range_to, required=True)
    locale_origin = fields.Many2one("res.lang", string="Locale Origin", required=True, default=_default_locale_origin)
    batch_size = fields.Integer(string="Batch Size", default=_default_batch_size, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        string="State",
        default="draft",
        required=True,
    )
    locked = fields.Boolean(string="Locked", default=False)
    locked_reason = fields.Text(string="Locked Reason")

    queue_job_minimum_size = fields.Integer(
        string="Queue Job Minimum Size",
        default=_default_queue_job_minimum_size,
    )
    use_job_queue = fields.Boolean(
        string="Use Job Queue",
        compute="_compute_use_job_queue",
    )

    def generate_demo_data(self):
        self.ensure_one()
        fake = Faker(self.locale_origin.code)
        if not self.use_job_queue:
            self.state = "in_progress"
            self.locked = True
            self.locked_reason = "Data generation in progress..."
            for _ in range(self.number_of_groups):
                group_vals = self.get_group_vals(fake)
                group = self.env["res.partner"].create(group_vals)
                self.create_ids(fake, group)
                num_members = fake.random_int(self.members_range_from, self.members_range_to)
                members = []
                have_head_member = False
                for _ in range(num_members):
                    is_head_member = random.choice([True, False]) if not have_head_member else False
                    individual_vals = self.get_individual_vals(fake)
                    individual = self.env["g2p.individual"].create(individual_vals)
                    self.create_ids(fake, individual)
                    membership_vals = self.get_group_membership_vals(fake, group, individual)
                    if is_head_member:
                        have_head_member = True
                        membership_vals["kind"] = self.env.ref("g2p_group_membership.group_membership_kind_head").id
                    members.append((4, membership_vals))
                if members:
                    self.env["g2p.group.membership"].create(members)

            self.state = "completed"
            self.locked = False
            self.locked_reason = "Data generation completed."

    def get_group_vals(self, fake):
        registration_date = self.get_random_date(
            fake,
            datefrom=fields.Date.today().replace(year=fields.Date.today().year - 5),
            dateto=fields.Date.today(),
        )

        group_vals = {
            "name": fake.company(),
            "is_registrant": True,
            "is_group": True,
            "registration_date": registration_date,
            "create_date": registration_date,
        }

        return group_vals

    def get_individual_vals(self, fake):
        birth_date = self.get_random_date(
            fake,
            datefrom=fields.Date.today().replace(year=fields.Date.today().year - 70),
            dateto=fields.Date.today().replace(year=fields.Date.today().year - 1),
        )
        registration_date = self.get_random_date(
            fake,
            datefrom=birth_date.replace(year=birth_date.year + 1),
            dateto=fields.Date.today(),
        )
        gender = random.choice(self.GENDERS)
        gender_id = self.get_gender_id(gender)
        first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
        last_name = fake.last_name()
        name = f"{first_name} {last_name}"

        individual_vals = {
            "name": name,
            "family_name": last_name,
            "given_name": first_name,
            "is_registrant": True,
            "is_group": False,
            "gender": gender_id,
            "birthdate": birth_date,
            "registration_date": registration_date,
        }
        return individual_vals

    def get_group_membership_vals(self, fake, group, individual):
        start_date = self.get_random_date(
            fake,
            datefrom=group.registration_date,
            dateto=fields.Date.today(),
        )
        return {
            "group": group.id,
            "individual": individual.id,
            "start_date": start_date,
        }

    def get_gender_id(self, gender):
        gender_id = self.env["gender.type"].search(["|", ("value", "=", gender), ("code", "=", gender)], limit=1)
        if not gender_id:
            gender_id = self.env["gender.type"].create({"value": gender, "code": gender})
        return gender_id.id

    def get_gender(self, gender):
        return self.env["gender.type"].search([("name", "=", gender)], limit=1).id

    def get_random_date(self, fake, datefrom, dateto):
        return fake.date_between_dates(date_start=datefrom, date_end=dateto)

    def get_id_type(self, id_type):
        id_type_id = self.env["g2p.id.type"].search([("name", "=", id_type)], limit=1)
        if not id_type_id:
            id_type_id = self.env["g2p.id.type"].create(
                {
                    "name": id_type,
                }
            )
        return id_type_id.id

    def create_ids(self, fake, registrant):
        id_type = random.choice(self.ID_TYPES_GROUP if registrant.is_group else self.ID_TYPES_INDIVIDUAL)
        id_type_id = self.get_id_type(id_type)
        id_number = fake.bothify(text="??######")
        issue_date = self.get_random_date(
            fake,
            datefrom=registrant.registration_date,
            dateto=fields.Date.today(),
        )
        id_expiry_date = self.get_random_date(
            fake,
            datefrom=issue_date.replace(year=issue_date.year + 1),
            dateto=issue_date.replace(year=issue_date.year + 10),
        )

        id_vals = {
            "partner_id": registrant.id,
            "id_type": id_type_id,
            "value": id_number,
            "expiry_date": id_expiry_date,
        }
        self.env["g2p.reg.id"].create(id_vals)

    def refresh_page(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def _compute_use_job_queue(self):
        for rec in self:
            rec.use_job_queue = rec.number_of_groups >= rec.queue_job_minimum_size
