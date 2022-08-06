# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class G2PMembershipGroup(models.Model):
    _inherit = "res.partner"

    group_membership_ids = fields.One2many(
        "g2p.group.membership", "group", "Group Members"
    )

    def count_individuals(self, kinds=None, criteria=None):
        """Count individuals based on kinds and criterias

        This returns the total number of rows produced by the SQL query
        from the query_members_aggregate function.

        :param kinds: membership kinds
        :param criteria: domain filter
        :type kinds: list
        :type criteria: string
        :returns: len(res_ids)
        :rtype: int

        :Example:

            var = self.count_individuals(
                kinds=["Head of Household","Alternate Recipient"],
                criteria="[('gender','=','Female')]"
            )

        """
        self.ensure_one()
        membership_kind_domain = None
        individual_domain = None
        if self.group_membership_ids:
            if kinds:
                membership_kind_domain = [("name", "in", kinds)]
        else:
            return 0

        if criteria is not None:
            individual_domain = criteria

        res_ids = self.query_members_aggregate(
            membership_kind_domain, individual_domain
        )
        return len(res_ids)

    def query_members_aggregate(
        self, membership_kind_domain=None, individual_domain=None
    ):
        domain = [("is_registrant", "=", True), ("is_group", "=", True)]
        query_obj = self.env["res.partner"]._where_calc(domain)

        membership_alias = query_obj.left_join(
            "res_partner", "id", "g2p_group_membership", "group", "id"
        )
        individual_alias = query_obj.left_join(
            membership_alias, "individual", "res_partner", "id", "individual"
        )
        membership_kind_rel_alias = query_obj.left_join(
            membership_alias,
            "id",
            "g2p_group_membership_g2p_group_membership_kind_rel",
            "g2p_group_membership_id",
            "id",
        )
        rel_kind_alias = query_obj.left_join(
            membership_kind_rel_alias,
            "g2p_group_membership_kind_id",
            "g2p_group_membership_kind",
            "id",
            "id",
        )

        # Build where clause for the membership_alias
        membership_query_obj = expression.expression(
            model=self.env["g2p.group.membership"],
            domain=[("end_date", "=", None), ("group", "=", self.id)],
            alias=membership_alias,
        ).query
        (
            membership_from_clause,
            membership_where_clause,
            membership_where_params,
        ) = membership_query_obj.get_sql()
        # _logger.info("SQL DEBUG: Membership Kind Query: From:%s, Where:%s, Params:%s" %
        #   (membership_from_clause,membership_where_clause,membership_where_params))
        query_obj.add_where(membership_where_clause, membership_where_params)

        if membership_kind_domain:
            membership_kind_query_obj = expression.expression(
                model=self.env["g2p.group.membership.kind"],
                domain=membership_kind_domain,
                alias=rel_kind_alias,
            ).query
            (
                membership_kind_from_clause,
                membership_kind_where_clause,
                membership_kind_where_params,
            ) = membership_kind_query_obj.get_sql()
            # _logger.info("SQL DEBUG: Membership Kind Query: From:%s, Where:%s, Params:%s" %
            #   (membership_kind_from_clause,membership_kind_where_clause,membership_kind_where_params))
            query_obj.add_where(
                membership_kind_where_clause, membership_kind_where_params
            )

        if individual_domain:
            individual_query_obj = expression.expression(
                model=self.env["res.partner"],
                domain=individual_domain,
                alias=individual_alias,
            ).query
            (
                individual_from_clause,
                individual_where_clause,
                individual_where_params,
            ) = individual_query_obj.get_sql()
            # _logger.info("SQL DEBUG: Individual Query: From:%s, Where:%s, Params:%s" %
            #   (individual_from_clause,individual_where_clause,individual_where_params))
            query_obj.add_where(individual_where_clause, individual_where_params)

        select_query, select_params = query_obj.select()
        _logger.info(
            "SQL DEBUG: SQL query: %s, params: %s" % (select_query, select_params)
        )

        self._cr.execute(select_query, select_params)
        results = self._cr.dictfetchall()
        _logger.info("SQL DEBUG: SQL Query Result: %s" % results)
        return results
