# ABOUTME: Override res.users model to customize user-related branding
# ABOUTME: Removes Odoo-specific URLs and references from user menu

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _get_default_email_signature(self):
        """Override default email signature to remove Odoo branding"""
        return """<br/>
--<br/>
<span style="color: #1f497d; font-weight: bold;">OpenSPP Platform</span><br/>
<span style="color: #999999; font-size: 0.9em;">Open Source Social Protection Platform</span>
"""

    def _compute_odoo_account_url(self):
        """Override to remove Odoo account URL"""
        for user in self:
            user.odoo_account_url = False

    odoo_account_url = fields.Char(
        compute="_compute_odoo_account_url", string="Account URL", help="OpenSPP Account Management", readonly=True
    )
