# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError

FIELD_TYPES = [(key, key) for key in sorted(fields.Field.by_type)]


class OpenSPPCustomFieldsUI(models.Model):
    _inherit = "ir.model.fields"

    target_type = fields.Selection(
        selection=[("grp", "Group"), ("indv", "Individual")],
        default="grp",
    )
    field_category = fields.Selection(
        selection=[("cst", "Custom"), ("ind", "Calculated")],
        default="cst",
    )
    prefix = fields.Char(compute="_compute_prefix")
    draft_name = fields.Char(string="Field Draft Name", index=True)
    kinds = fields.Many2many("g2p.group.membership.kind", string="Kind")
    has_presence = fields.Boolean("Presence", default=False)

    @api.depends("field_category", "target_type")
    def _compute_prefix(self):
        """
        This method is used to compute the Field Name prefix.
        :param field_category: The Field Category.
        :param target_type: The Target Type.
        :return: Computes the Prefix by the params.
        """
        self.prefix = "x_"
        if self.field_category:
            self.prefix += self.field_category + "_"
        if self.target_type:
            self.prefix += self.target_type

    @api.onchange("draft_name")
    def _onchange_draft_name(self):
        """
        This method is used to write the Field Name value by draft_name onchange.
        :param prefix: The Prefix.
        :param draft_name: The Draft Name.
        :return: Computes the Field Name by the params.
        """
        if self.prefix and self.draft_name:
            self.name = self.prefix + "_" + self.draft_name

        self.set_compute()

    @api.onchange("field_category")
    def _onchange_field_category(self):
        """
        This method is used to write the Compute Field by field_category onchange.
        :param field_category: The Field Category.
        :param prefix: The Prefix.
        :param draft_name: The Draft Name.
        :param name: The name.
        :return: Computes the Compute Field by the params.
        """
        for rec in self:
            rec.set_compute()

    @api.onchange("kinds")
    def _onchange_kinds(self):
        """
        This method is used to write the Compute Field by kinds onchange.
        :param kinds: The Kinds.
        :param prefix: The Prefix.
        :param draft_name: The Draft Name.
        :param name: The name.
        :return: Computes the Compute Field by the params.
        """
        for rec in self:
            rec.set_compute()

    @api.onchange("target_type")
    def _onchange_target_type(self):
        for rec in self:
            rec.set_compute()

    @api.onchange("has_presence")
    def _onchange_has_presence(self):
        """
        This method is used to change the ttype to 'boolean' if has_presence is true.
        :param ttype: The Field Type.
        :param has_presence: The Presence Field.
        :return: ttype.
        """

        for rec in self:
            rec.set_compute()

    def set_compute(self):
        for rec in self:
            name = ""
            rec.compute = None
            if rec.prefix:
                name = rec.prefix + "_"
            if rec.draft_name:
                name = name + rec.draft_name
            rec.name = name
            if rec.field_category == "ind":
                rec.compute = "kinds = None \n"
                if rec.kinds:
                    kind_ids = []
                    for rec_line in rec.kinds:
                        kind_id = str(rec_line.name)
                        kind_ids.append(kind_id)

                    rec.compute = "kinds = %s \n" % kind_ids
                rec.compute += "domain = []\n"
                if rec.has_presence:
                    rec.ttype = "boolean"
                    rec.compute += (
                        "self.compute_count_and_set_indicator('%s', kinds, domain, presence_only=True)" % name
                    )
                else:
                    rec.ttype = "integer"
                    rec.compute += "self.compute_count_and_set_indicator('%s', kinds, domain)" % name

    def _should_reload_view(self):
        """
        Check if the view should be reloaded after creating/updating custom fields.
        This is needed because custom fields modify the model registry.
        """
        return any(record.target_type for record in self)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to trigger page reload after field creation"""
        records = super().create(vals_list)
        # Trigger reload only for custom fields with target_type in UI context
        if self.env.context.get("params") and records._should_reload_view():
            return {
                "type": "ir.actions.client",
                "tag": "reload",
            }
        return records

    def write(self, vals):
        """Override write to trigger page reload after field update"""
        result = super().write(vals)
        # Trigger reload only for custom fields with target_type in UI context
        if self.env.context.get("params") and self._should_reload_view():
            return {
                "type": "ir.actions.client",
                "tag": "reload",
            }
        return result
