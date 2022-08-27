# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)

CHILDREN_AGE_LIMIT = 18
ELDERLY_AGE_LIMIT = 65


class G2PGroup(models.Model):
    _inherit = "res.partner"

    z_crt_grp_num_children = fields.Integer(
        "Number of children",
        compute="_compute_crt_grp_num_children",
        help="Number of children",
        store=True,
    )
    z_crt_grp_num_elderly = fields.Integer(
        "Number of eldery", compute="_compute_crt_grp_num_eldery", store=True
    )
    z_crt_grp_num_adults_male_not_elderly = fields.Integer(
        "Number of adults",
        compute="_compute_crt_grp_num_adults_male_not_elderly",
        store=True,
    )
    z_crt_grp_num_adults_female_not_elderly = fields.Integer(
        "Number of adults woman not elderly",
        compute="_compute_crt_grp_num_adults_female_not_elderly",
        store=True,
    )

    z_crt_grp_is_hh_with_disabled = fields.Boolean(
        "Is household disabled (mental or physical) members",
        compute="_compute_crt_grp_is_hh_with_disabled",
        help="HHs with disabled (mental or physical) members",
        store=True,
    )

    z_crt_grp_is_single_head_hh = fields.Boolean(
        "Is single-headed household",
        compute="_compute_crt_grp_is_single_head_hh",
        help="Single-headed HH - extracted from demographic data of "
        "HH adult members",
        store=True,
    )

    z_crt_grp_is_elderly_head_hh = fields.Boolean(
        "Is elderly-headed household",
        compute="_compute_crt_grp_is_eldery_head_hh",
        help="Elderly-headed HHs - "
        "extracted from demographic data of HH adult members",
        store=True,
    )

    def _compute_crt_grp_num_children(self):
        """
        Households (HH) with children
        Returns:

        """
        now = datetime.datetime.now()
        children = now - relativedelta(years=CHILDREN_AGE_LIMIT)
        indicator = [("birthdate", ">=", children)]
        self._compute_count_and_set("z_crt_grp_num_children", None, indicator)

    def _compute_crt_grp_num_eldery(self):
        """
        Number of Eldery in this household
        Returns:

        """
        now = datetime.datetime.now()
        indicator = [("birthdate", "<", now - relativedelta(years=ELDERLY_AGE_LIMIT))]
        self._compute_count_and_set("z_crt_grp_num_elderly", None, indicator)

    def _compute_crt_grp_num_adults_female_not_elderly(self):
        """
        Number of adults female in this household
        Returns:

        """
        now = datetime.datetime.now()
        indicator = [
            ("birthdate", ">=", now - relativedelta(years=ELDERLY_AGE_LIMIT)),
            ("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT)),
            ("gender", "=", "Female"),
        ]
        self._compute_count_and_set(
            "z_crt_grp_num_adults_female_not_elderly", None, indicator
        )

    def _compute_crt_grp_num_adults_male_not_elderly(self):
        """
        Number of adults male in this household
        Returns:

        """
        now = datetime.datetime.now()
        indicator = [
            ("birthdate", ">=", now - relativedelta(years=ELDERLY_AGE_LIMIT)),
            ("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT)),
            ("gender", "=", "Male"),
        ]
        self._compute_count_and_set(
            "z_crt_grp_num_adults_male_not_elderly", None, indicator
        )

    def _compute_crt_grp_is_single_head_hh(self):
        """
        single-headed HH - extracted from demographic data of HH adult members
        Returns:

        """
        # TODO: Should we exclude eldery?
        now = datetime.datetime.now()
        indicator = [("birthdate", "<", now - relativedelta(years=CHILDREN_AGE_LIMIT))]
        for record in self:
            if record["is_group"]:
                cnt = record.count_individuals(kinds=None, indicators=indicator)
                record["z_crt_grp_is_single_head_hh"] = cnt > 0
            else:
                record["z_crt_grp_is_single_head_hh"] = None

    def _compute_crt_grp_is_eldery_head_hh(self):
        """
        Elderly-headed HHs
        Returns:

        """
        now = datetime.datetime.now()
        indicator = [("birthdate", "<", now - relativedelta(years=ELDERLY_AGE_LIMIT))]
        # TODO: fix the iteration
        for record in self:
            if record["is_group"]:
                cnt = record.count_individuals(kinds=["Head"], indicators=indicator)
                _logger.info("cnt: %s", cnt)
                record.z_crt_grp_is_elderly_head_hh = cnt > 0
            else:
                record.z_crt_grp_is_elderly_head_hh = None

    def _compute_crt_grp_is_hh_with_disabled(self):
        """
        HHs with disabled (mental or physical) members
        """
        indicator = [("z_cst_ind_disability_level", ">", 0)]
        for record in self:
            if record["is_group"]:
                cnt = record.count_individuals(kinds=None, indicators=indicator)
                record.z_crt_grp_is_hh_with_disabled = cnt > 0
            else:
                record.z_crt_grp_is_hh_with_disabled = None
