# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.

import datetime
import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class ComputeIndicatorFieldsTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
                "birthdate": datetime.datetime.now(),
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
                "birthdate": datetime.datetime.now(),
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
                "birthdate": datetime.datetime.now(),
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
                "birthdate": datetime.datetime.now(),
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
                "birthdate": datetime.datetime.now(),
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
                "birthdate": datetime.datetime.now(),
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
                "gender": "Male",
                "z_cst_indv_cyclone_aug_2022_lost_livestock": True,
                "birthdate": datetime.datetime.now(),
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
                "birthdate": datetime.datetime.now(),
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
                "birthdate": datetime.datetime.now(),
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
                "birthdate": datetime.datetime.now(),
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
        members1 = []
        members1.append({"individual": cls.registrant_2.id})
        members1.append({"individual": cls.registrant_4.id})
        members1.append({"individual": cls.registrant_6.id})
        members1.append({"individual": cls.registrant_8.id})
        members1.append({"individual": cls.registrant_10.id})
        group1_members = []
        for val in members1:
            group1_members.append([0, 0, val])

        cls.group_1.write({"group_membership_ids": group1_members})
        members2 = []
        members2.append({"individual": cls.registrant_1.id})
        members2.append({"individual": cls.registrant_3.id})
        members2.append({"individual": cls.registrant_5.id})
        members2.append({"individual": cls.registrant_7.id})
        members2.append({"individual": cls.registrant_9.id})
        group2_members = []
        for val in members2:
            group2_members.append([0, 0, val])

        cls.group_2.write({"group_membership_ids": group2_members})

    def test_01_num_children(self):
        self.group_1._compute_ind_grp_num_children()
        self.assertEqual(
            self.group_1.z_ind_grp_num_children,
            5,
        )
        self.group_2._compute_ind_grp_num_children()
        self.assertEqual(
            self.group_2.z_ind_grp_num_children,
            5,
        )

    # Note: Disabled wrong tests
    # TODO: Fix below test cases
    # def test_02_num_eldery(self):
    #     now = datetime.datetime.now()
    #     birthdate = now - relativedelta(years=66)

    #     self.registrant_1.write({"birthdate": birthdate})
    #     self.registrant_3.write({"birthdate": birthdate})
    #     self.group_2._compute_ind_grp_num_eldery()
    #     self.assertEqual(
    #         self.group_2.z_ind_grp_num_elderly,
    #         2,
    #     )
    #     self.registrant_2.write({"birthdate": birthdate})
    #     self.group_1._compute_ind_grp_num_eldery()
    #     self.assertEqual(
    #         self.group_1.z_ind_grp_num_elderly,
    #         1,
    #     )

    # def test_03_num_adults_female_not_elderly(self):
    #     now = datetime.datetime.now()
    #     birthdate = now - relativedelta(years=20)

    #     self.registrant_1.write({"birthdate": birthdate})
    #     self.registrant_3.write({"birthdate": birthdate})
    #     self.group_2._compute_ind_grp_num_adults_female_not_elderly()
    #     self.assertEqual(
    #         self.group_2.z_ind_grp_num_adults_female_not_elderly,
    #         2,
    #     )
    #     self.registrant_2.write({"birthdate": birthdate})
    #     self.group_1._compute_ind_grp_num_adults_female_not_elderly()
    #     self.assertEqual(
    #         self.group_1.z_ind_grp_num_adults_female_not_elderly,
    #         1,
    #     )

    # def test_04_num_adults_male_not_elderly(self):
    #     now = datetime.datetime.now()
    #     birthdate = now - relativedelta(years=20)

    #     self.registrant_5.write({"birthdate": birthdate})
    #     self.registrant_7.write({"birthdate": birthdate})
    #     self.group_2._compute_ind_grp_num_adults_male_not_elderly()
    #     self.assertEqual(
    #         self.group_2.z_ind_grp_num_adults_male_not_elderly,
    #         2,
    #     )
    #     self.registrant_4.write({"birthdate": birthdate})
    #     self.group_1._compute_ind_grp_num_adults_male_not_elderly()
    #     self.assertEqual(
    #         self.group_1.z_ind_grp_num_adults_male_not_elderly,
    #         1,
    #     )


#     def test_05_num_cyclone_aug_2022_injured(self):
#         self.assertEqual(
#             self.group_2.z_ind_grp_num_cyclone_aug_2022_injured,
#             1,
#         )
#         self.assertEqual(
#             self.group_1.z_ind_grp_num_cyclone_aug_2022_injured,
#             1,
#         )

#     def test_06_num_receive_government_benefits(self):
#         self.assertEqual(
#             self.group_2.z_ind_grp_num_receive_government_benefits,
#             1,
#         )
#         self.assertEqual(
#             self.group_1.z_ind_grp_num_receive_government_benefits,
#             1,
#         )

#     def test_07_num_cyclone_aug_2022_lost_livestock(self):
#         self.assertEqual(
#             self.group_2.z_ind_grp_num_cyclone_aug_2022_lost_livestock,
#             1,
#         )
#         self.assertEqual(
#             self.group_1.z_ind_grp_num_cyclone_aug_2022_lost_livestock,
#             1,
#         )

#     def test_08_num_cyclone_aug_2022_lost_primary_source_income(self):
#         self.assertEqual(
#             self.group_2.z_ind_grp_num_cyclone_aug_2022_lost_primary_source_income,
#             1,
#         )
#         self.assertEqual(
#             self.group_1.z_ind_grp_num_cyclone_aug_2022_lost_primary_source_income,
#             1,
#         )

#     def test_09_num_disability(self):
#         self.assertEqual(
#             self.group_2.z_ind_grp_num_disability,
#             1,
#         )
#         self.assertEqual(
#             self.group_1.z_ind_grp_num_disability,
#             1,
#         )

#     def test_10_is_hh_with_disabled(self):
#         self.assertEqual(
#             self.group_2.z_ind_grp_is_hh_with_disabled,
#             True,
#         )
#         self.assertEqual(
#             self.group_1.z_ind_grp_is_hh_with_disabled,
#             True,
#         )

#     def test_11_is_single_head_hh(self):
#         self.assertEqual(
#             self.group_2.z_ind_grp_is_single_head_hh,
#             False,
#         )
#         self.assertEqual(
#             self.group_1.z_ind_grp_is_single_head_hh,
#             False,
#         )

#     def test_12_is_elderly_head_hh(self):
#         self.assertEqual(
#             self.group_2.z_ind_grp_is_elderly_head_hh,
#             False,
#         )
#         self.assertEqual(
#             self.group_1.z_ind_grp_is_elderly_head_hh,
#             False,
#         )
