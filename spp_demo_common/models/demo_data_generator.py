# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import datetime
import logging
import random
import re

from faker import Faker

from odoo import fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group

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
        country = self.env.user.company_id.country_id
        if country:
            return country.id
        return self.env.ref("base.us").id

    def _default_queue_job_minimum_size(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.queue_job_minimum_size", 500))

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
    locale_origin = fields.Many2one(
        "res.country", string="Locale Origin", required=True, default=_default_locale_origin
    )
    locale_origin_faker_locale = fields.Char(string="Locale Origin Faker Locale", related="locale_origin.faker_locale")
    batch_size = fields.Integer(string="Batch Size", default=_default_batch_size, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        string="State",
        default="draft",
        required=True,
    )
    group_type_id = fields.Many2one("g2p.group.kind", string="Group Type")
    id_type_ids = fields.One2many("spp.demo.data.id.types", "demo_data_generator_id", string="ID Types")
    bank_type_ids = fields.One2many("spp.demo.data.bank.types", "demo_data_generator_id", string="Bank Types")
    percentage_with_bank_account = fields.Integer(string="% with Banks", default=100, required=True)
    percentage_with_ids = fields.Integer(string="% with IDs", default=100, required=True)
    percentage_with_gps = fields.Integer(string="% with GPS Coordinates", default=100, required=True)

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
    generated_group_ids = fields.One2many(
        "res.partner",
        "demo_data_group_generator_id",
        string="Generated Registrants",
        readonly=True,
    )
    generated_individual_ids = fields.One2many(
        "res.partner",
        "demo_data_individual_generator_id",
        string="Generated Individuals",
        readonly=True,
    )

    def generate_demo_data(self):
        self.ensure_one()
        faker_code = self.locale_origin.faker_locale or "en_US"
        fake = Faker(faker_code)
        if self.members_range_from > self.members_range_to:
            self.members_range_from = self._default_members_range_from()
            self.members_range_to = self._default_members_range_to()
            raise ValidationError(
                "Members per Group (From) cannot be greater than Members per Group (To)."
                " Resetting to default values."
            )

        self.state = "in_progress"
        self.locked = True
        self.locked_reason = "Data generation in progress..."
        if not self.use_job_queue:
            for _ in range(self.number_of_groups):
                self._generate_demo_data(fake)
            self.state = "completed"
            self.locked = False
            message = "The data generation has been completed."
            self.locked_reason = message
            kind = "success"
        else:
            self._async_generate_demo_data()
            message = "The data generation has been started and is running in the background."
            kind = "info"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Data Generation",
                "message": message,
                "sticky": False,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def _generate_demo_data(self, fake):
        group = self.generate_groups(fake)
        num_members = fake.random_int(self.members_range_from, self.members_range_to)
        have_head_member = False
        new_group_name = False
        for _ in range(num_members):
            head_membership = self.head_member_getter(group)
            is_head_member = random.choice([True, False]) if not have_head_member else False

            # Check if last member and no head member assigned yet
            if _ == num_members - 1 and not have_head_member:
                is_head_member = True

            individual = self.generate_individuals(fake)
            membership_vals = self.get_group_membership_vals(fake, group, individual)
            if is_head_member and not head_membership:
                have_head_member = True
                new_group_name = individual.family_name
                group.name = new_group_name
                membership_vals["kind"] = [(4, self.env.ref("g2p_registry_membership.group_membership_kind_head").id)]

            self.env["g2p.group.membership"].create(membership_vals)
    
    def head_member_getter(self, group):
        memberships = self.env["g2p.group.membership"].search([("group", "=", group.id)])
        head_kind = self.env.ref("g2p_registry_membership.group_membership_kind_head")
        head_membership = memberships.filtered(lambda x: head_kind in x.kind)
        return head_membership

    def _async_generate_demo_data(self):
        jobs = []
        batch_size = self.batch_size
        batches = [
            (start, min(start + batch_size, self.number_of_groups))
            for start in range(0, self.number_of_groups, batch_size)
        ]
        for batch in batches:
            jobs.append(self.delayable()._process_batch(batch))
        main_job = group(*jobs)
        main_job.on_done(self.delayable()._mark_done())
        main_job.delay()

    def _process_batch(self, batch):
        self.ensure_one()
        faker_code = self.locale_origin.faker_locale or "en_US"
        fake = Faker(faker_code)
        for _ in range(batch[0], batch[1]):
            self._generate_demo_data(fake)

    def _mark_done(self):
        self.state = "completed"
        self.locked = False
        message = "The data generation has been completed."
        self.locked_reason = message

    def generate_groups(self, fake):
        group_vals = self.get_group_vals(fake)
        group = self.env["res.partner"].create(group_vals)
        self.create_ids(fake, group)
        self.create_phone_numbers(fake, group)
        self.create_bank_accounts(fake, group)
        self.create_gps_coordinates(fake, group)
        return group

    def generate_individuals(self, fake):
        individual_vals = self.get_individual_vals(fake)
        individual = self.env["res.partner"].create(individual_vals)
        self.create_ids(fake, individual)
        self.create_phone_numbers(fake, individual)
        self.create_bank_accounts(fake, individual)
        self.create_gps_coordinates(fake, individual)
        return individual

    def get_group_vals(self, fake):
        registration_date = self.get_random_date(
            fake,
            datefrom=fields.Date.today().replace(year=fields.Date.today().year - 5),
            dateto=fields.Date.today(),
        )
        address = fake.address()

        group_vals = {
            "demo_data_group_generator_id": self.id,
            "name": fake.company(),
            "is_registrant": True,
            "is_group": True,
            "registration_date": registration_date,
            "create_date": registration_date,
            "address": address,
        }
        if self.group_type_id:
            group_vals["kind"] = self.group_type_id.id
        else:
            group_types = self.env["g2p.group.kind"].search([])
            if group_types:
                group_vals["kind"] = random.choice(group_types).id

        return group_vals

    def get_individual_vals(self, fake):
        birth_date = self.get_random_date(
            fake,
            datefrom=fields.Date.today().replace(year=fields.Date.today().year - 50),
            dateto=fields.Date.today().replace(year=fields.Date.today().year - 1),
        )
        registration_date = self.get_random_date(
            fake,
            datefrom=birth_date + datetime.timedelta(days=365),
            dateto=fields.Date.today(),
        )
        gender = random.choice(self.GENDERS)
        gender_id = self.get_gender_id(gender)
        first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
        last_name = fake.last_name()
        name = f"{first_name} {last_name}"

        address = fake.address()

        individual_vals = {
            "demo_data_individual_generator_id": self.id,
            "name": name,
            "family_name": last_name,
            "given_name": first_name,
            "is_registrant": True,
            "is_group": False,
            "gender": gender_id,
            "birthdate": birth_date,
            "registration_date": registration_date,
            "create_date": registration_date,
            "address": address,
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

    def get_id_type(self, target_type):
        if self.id_type_ids:
            id_type = self.env["spp.demo.data.id.types"].search(
                [("target_type", "=", target_type), ("demo_data_generator_id", "=", self.id)]
            )
            if id_type:
                if len(self.id_type_ids) == 1:
                    return id_type.name.id, id_type.name.id_validation
                random_id = random.choice(id_type.name)
                return random_id.id, random_id.id_validation
            return None, None

        id_type_id = self.env["g2p.id.type"].search([])
        if id_type_id:
            id_type = random.choice(id_type_id)
            return id_type.id if len(id_type_id) > 1 else id_type.id, id_type.id_validation

        return None, None

    def generate_id_from_regex(self, regex_pattern):  # noqa: C901
        """
        Generate a string that matches the given regex pattern.
        Supports common regex patterns used in ID validation.
        """
        _logger.info(f"Generating ID from regex: {regex_pattern}")
        if not regex_pattern:
            return None

        # Remove anchors if present
        pattern = regex_pattern.strip()
        pattern = re.sub(r"^\^", "", pattern)
        pattern = re.sub(r"\$$", "", pattern)

        result = []
        i = 0

        while i < len(pattern):
            char = pattern[i]

            # Handle character classes [...]
            if char == "[":
                end = pattern.index("]", i)
                char_class = pattern[i + 1 : end]
                i = end + 1

                # Check for quantifier immediately after ]
                count = 1
                if i < len(pattern) and pattern[i] == "{":
                    q_end = pattern.index("}", i)
                    quantifier = pattern[i + 1 : q_end]

                    if "," in quantifier:
                        min_c, max_c = quantifier.split(",")
                        min_c = int(min_c) if min_c else 0
                        max_c = int(max_c) if max_c else min_c + 5
                    else:
                        min_c = max_c = int(quantifier)

                    count = random.randint(min_c, max_c)
                    i = q_end + 1

                # Generate characters based on character class
                for _ in range(count):
                    # Handle negation [^...]
                    if char_class.startswith("^"):
                        result.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
                    # Handle ranges like [A-Z], [0-9], [a-z]
                    elif "-" in char_class and len(char_class) == 3 and char_class[1] == "-":
                        start_char = ord(char_class[0])
                        end_char = ord(char_class[2])
                        result.append(chr(random.randint(start_char, end_char)))
                    # Handle explicit character list [ABC123]
                    else:
                        result.append(random.choice(char_class))

            # Handle backslash shortcuts
            elif char == "\\" and i + 1 < len(pattern):
                next_char = pattern[i + 1]
                i += 2

                # Check for quantifier
                count = 1
                if i < len(pattern) and pattern[i] == "{":
                    q_end = pattern.index("}", i)
                    quantifier = pattern[i + 1 : q_end]

                    if "," in quantifier:
                        min_c, max_c = quantifier.split(",")
                        min_c = int(min_c) if min_c else 0
                        max_c = int(max_c) if max_c else min_c + 5
                    else:
                        min_c = max_c = int(quantifier)

                    count = random.randint(min_c, max_c)
                    i = q_end + 1

                # Generate based on shortcut type
                for _ in range(count):
                    if next_char == "d":  # Digit
                        result.append(str(random.randint(0, 9)))
                    elif next_char == "w":  # Word character
                        result.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"))
                    elif next_char == "D":  # Non-digit
                        result.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
                    elif next_char == "s":  # Whitespace
                        result.append(" ")
                    else:
                        result.append(next_char)

            # Handle dot (any character)
            elif char == ".":
                result.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
                i += 1

            # Handle quantifiers *, +, ? (for previous character)
            elif char in "*+?" and result:
                if char == "*":
                    count = random.randint(0, 5)
                elif char == "+":
                    count = random.randint(1, 5)
                else:  # ?
                    count = random.randint(0, 1)

                last_char = result[-1]
                result.extend([last_char] * (count - 1))
                i += 1

            # Regular literal character
            else:
                result.append(char)
                i += 1

        return "".join(result)

    def create_ids(self, fake, registrant):
        """
        Create IDs for registrants with dynamic ID number generation based on regex.
        """
        if random.uniform(0, 100) > self.percentage_with_ids:
            return

        id_type_id, id_validation = self.get_id_type("group" if registrant.is_group else "individual")

        if id_type_id:
            # Get the id_validation regex from id_type
            id_validation_regex = None
            if id_validation:
                id_validation_regex = id_validation
            _logger.info(f"ID Validation Regex: {id_validation_regex}")
            # Generate ID number based on regex or fallback to default
            if id_validation_regex:
                try:
                    while True:
                        id_number = self.generate_id_from_regex(id_validation_regex)

                        # Validate generated ID against the regex
                        if not re.match(id_validation_regex, id_number):
                            continue

                        break
                except Exception:
                    # Fallback if generation failed
                    id_number = fake.bothify(text="??######")
            else:
                # No regex provided, use default generation
                id_number = fake.bothify(text="??######")

            issue_date = self.get_random_date(
                fake,
                datefrom=registrant.registration_date,
                dateto=fields.Date.today(),
            )
            id_expiry_date = issue_date + datetime.timedelta(days=365)

            id_vals = {
                "partner_id": registrant.id,
                "id_type": id_type_id,
                "value": id_number,
                "expiry_date": id_expiry_date,
            }
            self.env["g2p.reg.id"].create(id_vals)

    def get_bank_type(self, target_type):
        if self.bank_type_ids:
            bank_type = self.env["spp.demo.data.bank.types"].search(
                [("target_type", "=", target_type), ("demo_data_generator_id", "=", self.id)]
            )
            if bank_type:
                if len(self.bank_type_ids) == 1:
                    return bank_type.name.id
                return random.choice(bank_type.name.ids)
            return None

        bank_type_id = self.env["res.bank"].search([])
        if bank_type_id:
            return random.choice(bank_type_id).id if len(bank_type_id) > 1 else bank_type_id.id

        return None

    def create_bank_accounts(self, fake, registrant):
        if random.uniform(0, 100) > self.percentage_with_bank_account:
            return
        bank_type_id = self.get_bank_type("group" if registrant.is_group else "individual")
        if bank_type_id:
            account_number = fake.bothify(text="??######")
            bank_account_vals = {
                "partner_id": registrant.id,
                "bank_id": bank_type_id,
                "acc_number": account_number,
            }
            self.env["res.partner.bank"].create(bank_account_vals)

    def generate_phone_number(self, fake):
        while True:
            try:
                phone_number = fake.phone_number()
            except Exception:
                try:
                    phone_number = fake.mobile_number()
                except Exception:
                    phone_number = f"+{random.randint(1000000000, 9999999999)}"

            # Accept only numbers, spaces, dashes, parentheses, and leading +
            cleaned = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if cleaned.startswith("+"):
                cleaned = cleaned[1:]
            if cleaned.isdigit():
                break
        return cleaned

    def create_phone_numbers(self, fake, registrant):
        num_phone_numbers = random.randint(1, 5)
        for _ in range(num_phone_numbers):
            phone_number = self.generate_phone_number(fake)
            date_collected = self.get_random_date(
                fake,
                datefrom=registrant.registration_date,
                dateto=fields.Date.today(),
            )
            phone_vals = {
                "partner_id": registrant.id,
                "phone_no": phone_number,
                "date_collected": date_collected,
            }
            self.env["g2p.phone.number"].create(phone_vals)
        registrant.phone_number_ids_change()

    def create_gps_coordinates(self, fake, registrant):
        if random.uniform(0, 100) > self.percentage_with_gps:
            return

        lat_min, lat_max = self.locale_origin.lat_min, self.locale_origin.lat_max
        lon_min, lon_max = self.locale_origin.lon_min, self.locale_origin.lon_max

        if None not in (lat_min, lat_max, lon_min, lon_max):
            latitude = round(random.uniform(lat_min, lat_max), 6)
            longitude = round(random.uniform(lon_min, lon_max), 6)
            registrant.gps_coordinates = f"{latitude}, {longitude}"

    def refresh_page(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def _compute_use_job_queue(self):
        for rec in self:
            rec.use_job_queue = rec.number_of_groups >= rec.queue_job_minimum_size


class SPPDemoDataIDTypes(models.Model):
    _name = "spp.demo.data.id.types"
    _description = "SPP Demo Data ID Types"

    name = fields.Many2one("g2p.id.type", string="ID Type", required=True)
    target_type = fields.Selection(
        [("individual", "Individual"), ("group", "Group")],
        string="Target Type",
        required=True,
    )
    demo_data_generator_id = fields.Many2one(
        "spp.demo.data.generator", string="Demo Data Generator", ondelete="cascade"
    )


class SPPDemoDataBankTypes(models.Model):
    _name = "spp.demo.data.bank.types"
    _description = "SPP Demo Data Bank Types"

    name = fields.Many2one("res.bank", string="Bank Type", required=True)
    target_type = fields.Selection(
        [("individual", "Individual"), ("group", "Group")],
        string="Target Type",
        default="individual",
        required=True,
    )
    demo_data_generator_id = fields.Many2one(
        "spp.demo.data.generator", string="Demo Data Generator", ondelete="cascade"
    )
