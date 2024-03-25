from odoo import fields, models


class SppTicket(models.Model):
    _name = "spp.ticket"
    _description = "Social Protection Program Ticket"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    ticket_type = fields.Selection(
        [
            ("inquiry", "Inquiry"),
            ("request", "Request"),
            ("complaint", "Complaint"),
        ],
        string="Type",
        required=True,
    )
    priority = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("urgent", "Urgent"),
        ],
        string="Priority",
        default="low",
    )
    status = fields.Selection(
        [
            ("new", "New"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="new",
    )
    assigned_to = fields.Many2one("res.users", string="Assigned To")
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    creation_date = fields.Datetime(string="Creation Date", default=fields.Datetime.now)
    resolution_date = fields.Datetime(string="Resolution Date")
    last_updated = fields.Datetime(string="Last Updated", default=fields.Datetime.now)
    tag_ids = fields.Many2many("spp.ticket.tag", string="Tags")


class SppTicketTag(models.Model):
    _name = "spp.ticket.tag"
    _description = "Social Protection Program Ticket Tag"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")
