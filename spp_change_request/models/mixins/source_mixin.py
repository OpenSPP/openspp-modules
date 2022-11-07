# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import _, fields, models


class ChangeRequestSourceMixin(models.AbstractModel):
    """Change Request Data Source mixin."""

    _name = "spp.change.request.source.mixin"
    _description = "Change Request Data Source Mixin"
    _rec_name = "change_request_id"

    registrant_id = fields.Many2one(
        "res.partner", "Registrant", domain=[("is_registrant", "=", True)]
    )
    change_request_id = fields.Many2one(
        "spp.change.request", "Change Request", required=True
    )

    validatedby_id = fields.Many2one(
        "res.users", "Last Validator", related="change_request_id.validatedby_id"
    )
    date_validated = fields.Datetime(related="change_request_id.date_validated")
    state = fields.Selection(
        related="change_request_id.state",
        string="Status",
        readonly=True,
    )

    def _update_registrant_id(self, res):
        for rec in res:
            if rec.registrant_id:
                rec.change_request_id.update({"registrant_id": rec.registrant_id.id})

    def _get_name(self):
        name = ""
        if self.family_name:
            name += self.family_name + ", "
        if self.given_name:
            name += self.given_name + " "
        if self.addl_name:
            name += self.addl_name + " "
        return name.title()

    def get_request_type_view_id(self):
        """
        Retrieve form view ID.
        :param self: The request.
        :return: form view ID
        """
        return (
            self.env["ir.ui.view"]
            .sudo()
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )

    def _update_live_data(self):
        """
        This method is used to apply the changes to models based on the type of change request.
        :param self: The request.
        :return:
        """
        raise NotImplementedError()

    def on_submit(self):
        for rec in self:
            rec._on_submit(rec.change_request_id)

    def _on_submit(self, request):
        """
        This method is used to submit the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        self.ensure_one()
        # Mark previous activity as 'done'
        request.last_activity_id.action_done()
        # Create validation activity
        activity_type = "spp_change_request.validation_activity"
        summary = _("For Validation")
        note = _(
            "The change request is now set for validation. Depending on the "
            + "validation sequence, this may be subjected to one or more validations."
        )
        activity = request._generate_activity(activity_type, summary, note)

        # Update change request
        name = self.env["ir.sequence"].next_by_code("spp.change.request.num")
        request.update(
            {
                "name": name,
                "date_requested": fields.Datetime.now(),
                "state": "pending",
                "last_activity_id": activity.id,
            }
        )

    def on_validate(self):
        for rec in self:
            rec._on_validate(rec.change_request_id)

    def _on_validate(self, request):
        """
        This method is used to validate the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        raise NotImplementedError()

    def apply(self):
        for rec in self:
            rec._apply(rec.change_request_id)

    def _apply(self, request):
        """
        This method is used to apply the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        self.ensure_one()
        # Apply Changes to Live Data
        self._update_live_data()
        # Update CR record
        request.update(
            {
                "appliedby_id": self.env.user,
                "date_applied": fields.Datetime.now(),
                "state": "applied",
            }
        )
        # Mark previous activity as 'done'
        request.last_activity_id.action_done()

    def on_reject(self):
        for rec in self:
            rec._on_reject(rec.change_request_id)

    def _on_reject(self, request):
        """
        This method is used to reject the change request.
        :param self: The request type.
        :param request: The request.
        :return:
        """
        self.ensure_one()
        request.update(
            {
                "state": "rejected",
            }
        )
        # Mark previous activity as 'done'
        request.last_activity_id.action_done()
