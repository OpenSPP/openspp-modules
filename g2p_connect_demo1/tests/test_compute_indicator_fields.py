# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class ComputeIndicatorFieldsTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(ComputeIndicatorFieldsTest, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Initial Setup of Variables
        # Injured during Cyclone Aug 2022
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "family_name": "Jaddranka",
                "given_name": "Heidi",
                "name": "Heidi Jaddranka",
                "is_group": False,
                "is_registrant": True,
                "gender": "Female",
                "z_cst_indv_cyclone_aug_2022_injured": True,
            }
        )
        cls.registrant_2 = cls.env["res.partner"].create(
            {
                "family_name": "Kleitos",
                "given_name": "Angus",
                "name": "Angus Kleitos",
                "is_group": False,
                "is_registrant": True,
                "gender": "Female",
                "z_cst_indv_cyclone_aug_2022_injured": True,
            }
        )

        # With Disability level
        cls.registrant_3 = cls.env["res.partner"].create(
            {
                "family_name": "Caratacos",
                "given_name": "Sora",
                "name": "Sora Caratacos",
                "is_group": False,
                "is_registrant": True,
                "gender": "Female",
                "z_cst_indv_disability_level": 5,
            }
        )
        cls.registrant_4 = cls.env["res.partner"].create(
            {
                "family_name": "Demophon",
                "given_name": "Amaphia",
                "name": "Amaphia Demophon",
                "is_group": False,
                "is_registrant": True,
                "gender": "Male",
                "z_cst_indv_disability_level": 10,
            }
        )

        # Received government benefits
        cls.registrant_5 = cls.env["res.partner"].create(
            {
                "family_name": "Liwayway",
                "given_name": "Bukang",
                "name": "Bukang Liwayway",
                "is_group": False,
                "is_registrant": True,
                "gender": "Male",
                "z_cst_indv_receive_government_benefits": True,
            }
        )
        cls.registrant_6 = cls.env["res.partner"].create(
            {
                "family_name": "Silim",
                "given_name": "Takip",
                "name": "Takip Silim",
                "is_group": False,
                "is_registrant": True,
                "gender": "Female",
                "z_cst_indv_receive_government_benefits": True,
            }
        )

        # Lost significant livestock during Cyclone Aug 2022
        cls.registrant_7 = cls.env["res.partner"].create(
            {
                "family_name": "Dela Cruz",
                "given_name": "Juan",
                "name": "Juan Dela Cruz",
                "is_group": False,
                "is_registrant": True,
                "gender": "Female",
                "z_cst_indv_cyclone_aug_2022_lost_livestock": True,
            }
        )
        cls.registrant_8 = cls.env["res.partner"].create(
            {
                "family_name": "Octavio",
                "given_name": "Felipe",
                "name": "Felipe Octavio",
                "is_group": False,
                "is_registrant": True,
                "gender": "Male",
                "z_cst_indv_cyclone_aug_2022_lost_livestock": True,
            }
        )

        # Lost primary source income during Cyclone Aug 2022
        cls.registrant_9 = cls.env["res.partner"].create(
            {
                "family_name": "Grande",
                "given_name": "Mariel",
                "name": "Mariel Grande",
                "is_group": False,
                "is_registrant": True,
                "gender": "Female",
                "z_cst_indv_cyclone_aug_2022_lost_primary_source_income": True,
            }
        )
        cls.registrant_10 = cls.env["res.partner"].create(
            {
                "family_name": "Bae",
                "given_name": "Marina",
                "name": "Marina Bae",
                "is_group": False,
                "is_registrant": True,
                "gender": "Female",
                "z_cst_indv_cyclone_aug_2022_lost_primary_source_income": True,
            }
        )

        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_group": True,
                "is_registrant": True,
            }
        )
        cls.group_2 = cls.env["res.partner"].create(
            {
                "name": "Group 2",
                "is_group": True,
                "is_registrant": True,
            }
        )
        cls.group_3 = cls.env["res.partner"].create(
            {
                "name": "Group 3",
                "is_group": True,
                "is_registrant": True,
            }
        )

    def test_01_add_members(self):
        self.group_1.write(
            {"group_membership_ids": [(0, 0, {"individual": self.registrant_1.id})]}
        )
        message = (
            "Membership Testing: Adding Group Member Failed! Result: %s Expecting: %s"
            % (
                self.group_1.group_membership_ids[0].individual.name,
                self.registrant_1.name,
            )
        )
        self.assertEqual(
            self.group_1.group_membership_ids[0].individual.id,
            self.registrant_1.id,
            message,
        )

    def test_02_assign_member(self):
        self.registrant_2.write(
            {"individual_membership_ids": [(0, 0, {"group": self.group_2.id})]}
        )
        message = (
            "Membership Testing: Assigning Member to Group Failed! Result %s Expecting %s"
            % (
                self.registrant_2.individual_membership_ids[0].group.id,
                self.group_2.id,
            )
        )
        self.assertEqual(
            self.registrant_2.individual_membership_ids[0].group.id,
            self.group_2.id,
            message,
        )
