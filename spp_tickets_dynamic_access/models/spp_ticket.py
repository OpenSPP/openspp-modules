from odoo import api, fields, models


class SPPTicket(models.Model):
    _name = "spp.ticket"  # Ensure this matches your actual model definition

    # Existing fields definition
    partner_id = fields.Many2one("res.partner", string="Partner", required=True, track_visibility="onchange")
    assigned_to = fields.Many2one("res.users", string="Assigned To", track_visibility="onchange")
    status = fields.Selection(
        [
            ("new", "New"),
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="new",
        track_visibility="onchange",
    )

    @api.model
    def create(self, vals):
        # Custom logic before creating a ticket
        ticket = super().create(vals)
        # Automatically grant access to the assigned support staff if any
        if ticket.assigned_to:
            ticket.partner_id.sudo().write({"support_staff_ids": [(4, ticket.assigned_to.id)]})
        return ticket

    def write(self, vals):
        # If the 'assigned_to' or 'status' field is changing, adjust access accordingly
        if "assigned_to" in vals or "status" in vals:
            new_assigned_id = vals.get("assigned_to")
            for record in self:
                # Remove access for the current assigned staff if the ticket is closed or reassigned
                if record.status in ["resolved", "closed"] or "assigned_to" in vals:
                    if record.assigned_to:
                        record.partner_id.sudo().write({"support_staff_ids": [(3, record.assigned_to.id)]})
                # Grant access to the new assigned staff
                if new_assigned_id:
                    record.partner_id.sudo().write({"support_staff_ids": [(4, new_assigned_id)]})
        return super().write(vals)
