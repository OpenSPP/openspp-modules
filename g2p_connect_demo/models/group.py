# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import collections
import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)

CHILDREN_AGE_LIMIT = 18
ELDERLY_AGE_LIMIT = 65


class G2PGroup(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "custom.filter.mixin"]

    z_ind_grp_num_children = fields.Integer(
        "Number of children",
        compute="_compute_ind_grp_num_children",
        help="Number of children",
        store=True,
        allow_filter=True,
    )
    z_ind_grp_num_elderly = fields.Integer("Number of eldery", compute="_compute_ind_grp_num_eldery", store=True)
    z_ind_grp_num_adults_male_not_elderly = fields.Integer(
        "Number of adults male not elderly",
        compute="_compute_ind_grp_num_adults_male_not_elderly",
        store=True,
        allow_filter=True,
    )
    z_ind_grp_num_adults_female_not_elderly = fields.Integer(
        "Number of adults woman not elderly",
        compute="_compute_ind_grp_num_adults_female_not_elderly",
        store=True,
        allow_filter=True,
    )
    z_ind_grp_num_cyclone_aug_2022_injured = fields.Integer(
        "Number of members injured during Cyclone Aug 2022",
        compute="_compute_ind_grp_num_cyclone_aug_2022_injured",
        help="Number of injured",
        store=True,
        allow_filter=True,
    )
    z_ind_grp_num_receive_government_benefits = fields.Integer(
        "Number of members received government benefits",
        compute="_compute_ind_grp_num_receive_government_benefits",
        help="Number of members received government benefits",
        store=True,
        allow_filter=True,
    )
    z_ind_grp_num_cyclone_aug_2022_lost_livestock = fields.Integer(
        "Number of members lost significant livestock during Cyclone Aug 2022",
        compute="_compute_ind_grp_num_cyclone_aug_2022_lost_livestock",
        help="Number of members lost significant livestock during Cyclone Aug 2022",
        store=True,
        allow_filter=True,
    )
    z_ind_grp_num_cyclone_aug_2022_lost_primary_source_income = fields.Integer(
        "Number of members lost primary source income during Cyclone Aug 2022",
        compute="_compute_ind_grp_num_cyclone_aug_2022_lost_primary_source_income",
        help="Number of members lost primary source income during Cyclone Aug 2022",
        store=True,
        allow_filter=True,
    )
    z_ind_grp_num_disability = fields.Integer(
        "Number of members with disability",
        compute="_compute_ind_grp_num_disability",
        help="Number of members with disability",
        store=True,
        allow_filter=True,
    )

    z_ind_grp_is_hh_with_disabled = fields.Boolean(
        "Is household disabled (mental or physical) members",
        compute="_compute_ind_grp_is_hh_with_disabled",
        help="HHs with disabled (mental or physical) members",
        store=True,
        allow_filter=True,
    )

    z_ind_grp_is_single_head_hh = fields.Boolean(
        "Is single-headed household",
        compute="_compute_ind_grp_is_single_head_hh",
        help="Single-headed HH - extracted from demographic data of " "HH adult members",
        store=True,
        allow_filter=True,
    )

    z_ind_grp_is_elderly_head_hh = fields.Boolean(
        "Is elderly-headed household",
        compute="_compute_ind_grp_is_eldery_head_hh",
        help="Elderly-headed HHs - " "extracted from demographic data of HH adult members",
        store=True,
        allow_filter=True,
    )

    z_ind_grp_num_single_child_less_36m_with_birth_cert = fields.Integer(
        "Number of Children of less than 36 months old with birth certificate",
        compute="_compute_ind_grp_single_child_less_36m_with_birth_cert",
        store=True,
        allow_filter=True,
    )

    z_ind_grp_num_twin_less_36m_with_birth_cert = fields.Integer(
        "Number of twins of less than 36 months old with birth certificate",
        compute="_compute_ind_grp_twin_less_36m_with_birth_cert",
        store=True,
        allow_filter=True,
    )

    z_ind_grp_num_triplets_more_less_36m_with_birth_cert = fields.Integer(
        "Number of triplets or more of less than 36 months old with birth certificate",
        compute="_compute_ind_grp_triplets_more_less_36m_with_birth_cert",
        store=True,
        allow_filter=True,
    )

    def _compute_ind_grp_single_child_less_36m_with_birth_cert(self):
        for rec in self:
            rec.z_ind_grp_num_single_child_less_36m_with_birth_cert = rec._count_child_by_group(1)

    def _compute_ind_grp_twin_less_36m_with_birth_cert(self):
        for rec in self:
            rec.z_ind_grp_num_twin_less_36m_with_birth_cert = rec._count_child_by_group(2)

    def _compute_ind_grp_triplets_more_less_36m_with_birth_cert(self):
        for rec in self:
            rec.z_ind_grp_num_triplets_more_less_36m_with_birth_cert = rec._count_child_by_group(3)

    def _count_child_by_group(self, group):
        self.ensure_one()
        # basic implementation
        now = datetime.datetime.now()
        children = now - relativedelta(years=CHILDREN_AGE_LIMIT)

        count_by_type = {}
        domain = [
            ("birthdate", ">=", children),
            ("z_cst_indv_has_birth_certificate", "=", True),
        ]

        children_birthdate = self.group_membership_ids.individual.filtered_domain(domain).mapped("birthdate")
        logging.info(children_birthdate)
        # basic identifying of twins
        children_birthdate = sorted(children_birthdate)
        children_birthdate = map(lambda x: x.strftime("%Y-%m-%d"), children_birthdate)
        count_by_date = collections.Counter(children_birthdate)

        for _date, count in count_by_date.items():
            count_by_type.setdefault(count, 0)
            count_by_type[count] += 1
        if group == 3:
            return sum(count_by_type.values()) - count_by_type.get(1, 0) - count_by_type.get(2, 0)
        return count_by_type.get(group, 0)

    def _compute_ind_grp_num_children(self):
        """
        Households (HH) with children
        Returns:

        """
        now = datetime.datetime.now()
        children = now - relativedelta(years=CHILDREN_AGE_LIMIT)
        domain = [("birthdate", ">=", children)]
        self.compute_count_and_set_indicator("z_ind_grp_num_children", None, domain)

    def _compute_ind_grp_num_eldery(self):
        """
        Number of Eldery in this household
        Returns:

        """
        now = datetime.datetime.now()
        domain = [("birthdate", "<", now - relativedelta(years=ELDERLY_AGE_LIMIT))]
        self.compute_count_and_set_indicator("z_ind_grp_num_elderly", None, domain)

    def _compute_ind_grp_num_adults_female_not_elderly(self):
        """
        Number of adults female in this household
        Returns:

        """
        now = datetime.datetime.now()
        domain = [
            ("birthdate", ">=", now - relativedelta(years=ELDERLY_AGE_LIMIT)),
            ("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT)),
            ("gender", "=", "Female"),
        ]
        self.compute_count_and_set_indicator("z_ind_grp_num_adults_female_not_elderly", None, domain)

    def _compute_ind_grp_num_adults_male_not_elderly(self):
        """
        Number of adults male in this household
        Returns:

        """
        now = datetime.datetime.now()
        domain = [
            ("birthdate", ">=", now - relativedelta(years=ELDERLY_AGE_LIMIT)),
            ("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT)),
            ("gender", "=", "Male"),
        ]
        self.compute_count_and_set_indicator("z_ind_grp_num_adults_male_not_elderly", None, domain)

    def _compute_ind_grp_num_cyclone_aug_2022_injured(self):
        """
        Number of members injured during Cyclone Aug 2022
        Returns:

        """
        domain = [("z_cst_indv_cyclone_aug_2022_injured", "=", True)]
        self.compute_count_and_set_indicator("z_ind_grp_num_cyclone_aug_2022_injured", None, domain)

    def _compute_ind_grp_num_receive_government_benefits(self):
        """
        Number of members received government benefits
        Returns:

        """
        domain = [("z_cst_indv_receive_government_benefits", "=", True)]
        self.compute_count_and_set_indicator("z_ind_grp_num_receive_government_benefits", None, domain)

    def _compute_ind_grp_num_cyclone_aug_2022_lost_livestock(self):
        """
        Number of members lost significant livestock during Cyclone Aug 2022
        Returns:

        """
        domain = [("z_cst_indv_cyclone_aug_2022_lost_livestock", "=", True)]
        self.compute_count_and_set_indicator("z_ind_grp_num_cyclone_aug_2022_lost_livestock", None, domain)

    def _compute_ind_grp_num_cyclone_aug_2022_lost_primary_source_income(self):
        """
        Number of members received government benefits
        Returns:

        """
        domain = [("z_cst_indv_cyclone_aug_2022_lost_primary_source_income", "=", True)]
        self.compute_count_and_set_indicator("z_ind_grp_num_cyclone_aug_2022_lost_primary_source_income", None, domain)

    def _compute_ind_grp_num_disability(self):
        """
        Number of members with disability
        Returns:

        """
        domain = [("z_cst_indv_disability_level", ">", 0)]
        self.compute_count_and_set_indicator("z_ind_grp_num_disability", None, domain)

    def _compute_ind_grp_is_single_head_hh(self):
        """
        single-headed HH - extracted from demographic data of HH adult members
        Returns:

        """
        # TODO: This does not work as expected anymore @Emjay0921 it should be only when there is one adult only
        now = datetime.datetime.now()
        domain = [("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT))]
        self.compute_count_and_set_indicator("z_ind_grp_is_single_head_hh", None, domain, presence_only=True)

    def _compute_ind_grp_is_eldery_head_hh(self):
        """
        Elderly-headed HHs
        Returns:

        """
        now = datetime.datetime.now()
        domain = [("birthdate", "<", now - relativedelta(years=ELDERLY_AGE_LIMIT))]
        self.compute_count_and_set_indicator("z_ind_grp_is_elderly_head_hh", ["Head"], domain, presence_only=True)

    def _compute_ind_grp_is_hh_with_disabled(self):
        """
        HHs with disabled (mental or physical) members
        """
        domain = [("z_cst_indv_disability_level", ">", 0)]
        self.compute_count_and_set_indicator("z_ind_grp_is_hh_with_disabled", None, domain, presence_only=True)
