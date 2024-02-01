# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import datetime
import logging
import math
import random

from dateutil.relativedelta import relativedelta
from faker import Faker

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class OpenG2PGenerateChangeRequestData(models.Model):
    _name = "g2p.generate.change.request.data"

    name = fields.Char()
    num_crs = fields.Integer("Number of CRs", default=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("generate", "Generated"),
        ],
        default="draft",
    )

    def generate_sample_data(self):
        # Get 50 registrants to be selected randomly in the CR registrant_id
        registrants = self.env["res.partner"].search(
            [
                ("is_registrant", "=", True),
                ("is_group", "=", True),
                ("group_membership_ids", "!=", False),
            ],
            limit=50,
        )
        if registrants:
            registrant_ids = registrants.mapped("id")
        else:
            raise UserError(_("There are no registrants that can be used for generating change requests."))
        # Get all membership kinds
        membership_kinds = self.env["g2p.group.membership.kind"].search([])
        if membership_kinds:
            membership_kinds.mapped("id")
        else:
            raise UserError(_("There are no membership kinds defined."))

        batches = math.ceil(self.num_crs / 1000)
        jobs = []
        for _i in range(0, batches):
            jobs.append(
                self.delayable()._generate_sample_data(
                    res_id=self.id,
                    registrant_ids=registrant_ids,
                    membership_kinds=membership_kinds,
                )
            )
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

        registrants = kwargs.get("registrant_ids")
        membership_kinds = kwargs.get("membership_kinds")
        num_crs = min(res.num_crs, 1000)

        cr_sample_data = []
        for i in range(0, num_crs):
            # Prepare spp.change.request fields data
            request_type = "spp.change.request.add.children"
            registrant_id = random.choice(registrants)

            # Get applicants based on registrant_id
            registrant = self.env["res.partner"].search([("id", "=", registrant_id)])[0]
            if registrant.lang:
                lang = registrant.lang
            else:
                lang = registrant.company_id.partner_id.lang
            fake = Faker(lang)
            _logger.debug("Registrant Name: %s" % registrant.name)
            _logger.debug("Registrant Language: %s" % lang)
            applicant_ids = registrant.group_membership_ids.mapped("individual.id")
            applicant_id = random.choice(applicant_ids)

            # TODO: Fix error in phone number format
            applicant = self.env["res.partner"].search([("id", "=", applicant_id)])
            if applicant.phone:
                applicant_phone = applicant.phone
            else:
                applicant_phone = fake.phone_number()

            cr_vals = {
                "request_type": request_type,
                "registrant_id": registrant_id,
                "applicant_id": applicant_id,
                "applicant_phone": applicant_phone,
            }
            _logger.debug(f"Processing #{i} Data: {cr_vals}")
            cr_sample_data.append(cr_vals)

        _logger.debug(f"Sample CR Data: Total: {len(cr_sample_data)} \nData: {cr_sample_data}")

        generated_crs = self.env["spp.change.request"].create(cr_sample_data)
        generated_crs.create_request_detail_demo()

        # Store spp.change.reques.add.children data
        for crd in generated_crs:
            family_name = fake.last_name()
            gender = random.choice(["Female", "Male"] * 50)
            given_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
            addl_name = fake.last_name()
            birth_place = fake.address()
            birthdate_not_exact = random.choice([True, False] * 50)
            date_start = datetime.datetime.now() - relativedelta(years=100)
            date_end = datetime.datetime.now()
            birthdate = fake.date_between_dates(date_start=date_start, date_end=date_end).isoformat()
            # phone = fake.phone_number()
            uid_number = str(random.randint(100000000000, 999999999999))
            kind = random.choice(membership_kinds)
            applicant_relation = random.choice(["father", "mother", "grandfather"] * 50)

            crd.request_type_ref_id.update(
                {
                    "family_name": family_name,
                    "given_name": given_name,
                    "addl_name": addl_name,
                    "gender": gender,
                    "birth_place": birth_place,
                    "birthdate_not_exact": birthdate_not_exact,
                    "birthdate": birthdate,
                    # "phone": phone,
                    "uid_number": uid_number,
                    "kind": kind,
                    "applicant_relation": applicant_relation,
                }
            )

    def mark_as_done(self):
        self.update({"state": "generate"})
