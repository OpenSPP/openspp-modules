# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import datetime
import hashlib
import logging
import math
import random

from dateutil.relativedelta import relativedelta
from faker import Faker

from odoo import api, fields, models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class OpenG2PGenerateData(models.Model):
    _name = "g2p.generate.data"

    name = fields.Char()
    num_groups = fields.Integer("Number of Groups", default=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("generate", "Generated"),
        ],
        default="draft",
    )

    def generate_sample_data(self):
        batches = math.ceil(self.num_groups / 1000)
        jobs = []
        for _i in range(0, batches):
            jobs.append(self.delayable()._generate_sample_data(res_id=self.id))
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_as_done())
        main_job.delay()

    @api.model
    def _generate_sample_data(self, **kwargs):
        """
        Generate sample data for testing
        Returns:
        """
        res_id = kwargs.get("res_id")
        res = self.browse(res_id)
        locales = [
            # "cs_CZ",
            # "en_US",
            "id_ID",
            # "de_CH",
            # "ar_AA",
            # "de_DE",
            # "en_GB",
            # "en_IE",
            # "en_TH",
            # "es_ES",
            # "es_MX",
            # "fr_FR",
            # "hi_IN",
            # "hr_HR",
            # "it_IT",
            # "zh_CN",
        ]
        fake = Faker(locales)

        # sex_choice_range = ["Female", "Male"] * 50 + ["Other"]
        sex_choice_range = ["Female", "Male"] * 50
        age_group_range = ["A", "C", "N"] * 2 + ["E"]
        group_size_range = list(range(1, 2)) * 2 + list(range(3, 5)) * 4 + list(range(6, 8))

        group_membership_kind_head_id = self.env.ref("g2p_registry_membership.group_membership_kind_head").id
        group_kind_household_id = self.env.ref("g2p_registry_group.group_kind_household").id
        # group_kind_family_id = self.env.ref("g2p_registry_group.group_kind_family").id

        num_groups = min(res.num_groups, 1000)

        bank = self.env["res.bank"].search([("name", "=", "slcb")])
        if bank:
            bank_id = bank[0]
        else:
            vals = {"name": "slcb", "bic": "10010010"}
            # TODO set the country
            bank_id = self.env["res.bank"].create(vals)

        # Get area center ids
        center_areas = self.env["spp.area"].search([("parent_id", "!=", False)])
        center_area_ids = center_areas.mapped("id")

        for i in range(0, num_groups):
            locale = random.choice(locales)
            group_size = random.choice(group_size_range)
            last_name = fake[locale].last_name()

            registration_date = (
                fake[locale]
                .date_between_dates(
                    date_start=datetime.datetime.now() - relativedelta(weeks=4),
                    date_end=datetime.datetime.now(),
                )
                .isoformat()
            )

            head = res._generate_individual_data(
                fake[locale],
                last_name,
                sex_choice_range,
                ["A", "E"],
                registration_date,
                bank_id,
            )

            head["is_head"] = True

            group_id = "demo." + hashlib.md5(f"{last_name} {i}".encode()).hexdigest()

            group_kind = group_kind_household_id  # random.choice([group_kind_household_id, group_kind_family_id])

            bank_ids = []

            # Make sure we get a unique number
            while True:
                bank_number = str(random.randint(111111111, 9999999999))
                if not self.env["res.partner.bank"].search_count([("acc_number", "=", bank_number)]):
                    break

            val = {
                "bank_id": bank_id.id,
                "acc_number": bank_number,
            }
            bank_ids.append([0, 0, val])
            group = {
                "id": group_id,
                "name": last_name,
                "is_group": True,
                "is_registrant": True,
                "registration_date": registration_date,
                "kind": group_kind,
                "street": fake[locale].street_address(),
                "street2": fake[locale].street_name(),
                "city": fake[locale].city(),
                "zip": fake[locale].postcode(),
                "area_id": random.choice(center_area_ids),
                "bank_ids": bank_ids,
            }

            create_group_id = self.env["res.partner"].create(group)

            head["id"] = f"{group_id}-0"
            members = [head]

            for i in range(group_size - 1):
                data = res._generate_individual_data(
                    fake[locale],
                    last_name,
                    sex_choice_range,
                    age_group_range,
                    registration_date,
                    bank_id,
                )

                data["id"] = f"{group_id}-{i+1}"
                members.append(data)

            # add this on membership
            if random.randint(0, 2) == 0:
                members[0]["is_principal_recipient"] = True
            else:
                members[random.randint(0, group_size - 1)]["is_principal_recipient"] = True

            for member in members:
                is_head = True if (member and member.get("is_head")) else False
                is_principal_recipient = True if (member and member.get("is_principal_recipient")) else False

                if is_head:
                    member.pop("is_head", None)
                    member.pop("is_principal_recipient", None)
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                            "kind": [
                                (
                                    4,
                                    group_membership_kind_head_id,
                                )
                            ],
                        }
                    )

                elif is_principal_recipient:
                    member.pop("is_head", None)
                    member.pop("is_principal_recipient", None)
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                            "kind": [],
                        }
                    )

                else:
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                        }
                    )

        msg = "Task Queue called task: model [{}] and method [{}].".format(
            self._name,
            "_generate_sample_data",
        )
        _logger.info(msg)
        return {"result": msg, "res_model": self._name, "res_ids": [res_id]}
        # _logger.info("-" * 80)
        # _logger.info(json.dumps({"group": group, "members": members}, indent=4))

    def mark_as_done(self):
        self.update({"state": "generate"})

    def _generate_individual_data(
        self,
        fake,
        last_name,
        sex_choice_range,
        age_group_range,
        registration_date,
        bank_id,
    ):
        sex = random.choice(sex_choice_range)
        age_group = random.choice(age_group_range)
        first_name = fake.first_name_male() if sex == "Male" else fake.first_name_female()
        different_last_name = random.randint(0, 100) < 10
        if age_group == "N":
            date_start = datetime.datetime.now() - relativedelta(years=1)
            date_end = datetime.datetime.now()
        elif age_group == "C":
            date_start = datetime.datetime.now() - relativedelta(years=17)
            date_end = datetime.datetime.now()
        elif age_group == "A":
            date_start = datetime.datetime.now() - relativedelta(years=65)
            date_end = datetime.datetime.now() - relativedelta(years=18)
        else:
            date_start = datetime.datetime.now() - relativedelta(years=100)
            date_end = datetime.datetime.now() - relativedelta(years=65)

        if different_last_name:
            last_name = fake.last_name()

        injured = False
        if random.randint(0, 10) == 1:
            injured = True

        disability_level = 0
        if random.randint(0, 100) < 2:
            disability_level = random.randint(10, 100)

        gov_benefits = False
        if random.randint(0, 10) == 1:
            gov_benefits = True

        lost_livestock = False
        if random.randint(0, 5) == 1:
            lost_livestock = True

        lost_primary_source_income = False
        if random.randint(0, 3) == 1:
            lost_primary_source_income = True

        dob = fake.date_between_dates(date_start=date_start, date_end=date_end).isoformat()

        fullname = f"{first_name} {last_name}"
        bank_ids = []
        phone = ""
        # Do not give bank account to kids
        if age_group != "C":
            val = {
                "bank_id": bank_id.id,
                "acc_number": str(random.randint(1, 999999999)),
            }
            bank_ids.append([0, 0, val])
            phone = fake.phone_number()
        data = {
            "name": fullname,
            "given_name": first_name,
            "family_name": last_name,
            "gender": sex,
            "birthdate": dob,
            "is_registrant": True,
            "is_group": False,
            "phone": phone,
            "registration_date": registration_date,
            "z_cst_indv_cyclone_aug_2022_injured": injured,
            "z_cst_indv_disability_level": disability_level,
            "z_cst_indv_receive_government_benefits": gov_benefits,
            "z_cst_indv_cyclone_aug_2022_lost_livestock": lost_livestock,
            "z_cst_indv_cyclone_aug_2022_lost_primary_source_income": lost_primary_source_income,
            "street": fake.street_address(),
            "street2": fake.street_name(),
            "city": fake.city(),
            "zip": fake.postcode(),
            "bank_ids": bank_ids,
        }

        if phone:
            data["phone_number_ids"] = [[0, 0, {"phone_no": phone}]]

        return data
