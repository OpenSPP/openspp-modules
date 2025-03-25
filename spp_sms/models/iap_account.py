# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        [("odoo", "Odoo IAP"), ("sms_twilio", "Twilio"), ("sns_amazon", "Amazon SNS")],
        required=True,
        default="odoo",
    )
    sms_twilio_account_id = fields.Char(string="Account ID")
    sms_twilio_token_id = fields.Char(string="Token ID")
    sms_twilio_from = fields.Char(string="From")

    sns_amazon_key = fields.Char(string="Access Key")
    sns_amazon_secret = fields.Char(string="Secret Access Key")
    sns_amazon_region = fields.Char(string="Region")

    active_status = fields.Boolean(string="Active", default=True)
