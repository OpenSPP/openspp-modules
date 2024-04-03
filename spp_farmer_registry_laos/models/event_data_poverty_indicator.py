from odoo import fields, models


class OpenSPPEventDataPovertyIndicator(models.Model):
    _name = "spp.event.poverty.indicator"
    _description = "III. Poverty Indicator"

    type_of_housing = fields.Selection([("1", "Not Permanent"), ("2", "Medium permanent"), ("3", "Permanent")])
    atleast_1household_member_completed_sch = fields.Selection(
        [("1", "Yes"), ("2", "No")], string="At least one household member completed compulsory school"
    )
    there_are_children_attend_pri_sch = fields.Selection(
        [("1", "Yes"), ("2", "No"), ("3", "N/A (I have no children aged 6-10 years)")],
        string="There are children attend primary school",
    )
    there_are_children_attend_mid_sch = fields.Selection(
        [("1", "Yes"), ("2", "No"), ("3", "N/A (I have no children aged 11-13 years)")],
        string="There are children attend middle school",
    )
    access_to_electricity = fields.Selection(
        [
            ("1", "No Electricity"),
            ("2", "Private power generation (solar panel, generator, etc.)"),
            ("3", "Connected to power grid"),
        ],
        string="Access to Electricity",
    )
    access_to_basic_health_care = fields.Selection([("1", "Yes"), ("2", "No")], string="Access to Basic Health Care")
    access_to_internet = fields.Selection(
        [
            ("1", "No, internet accesses as the area has no mobile coverage"),
            ("2", "No internet accesses as the interviewee has no mobile phone (the area has mobile coverage)"),
            ("3", "Yes, have access to internet"),
        ],
        string="Access to Internet",
    )

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
