# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from odoo import fields, models

_logger = logging.getLogger(__name__)

TWILIO_ERROR_STATES = {
    21211: "invalid_to_number",
    21212: "invalid_from_number",
    21214: "cannot_be_reached",
    63038: "reached_rate_limit",
    21659: "invalid_from_number_mismatch",
    21267: "invalid_from_number_alphanumeric",
}


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
    sequence = fields.Integer(default=1)

    def twilio_send_sms_batch(self, messages):
        _logger.info("SMS Provider: %s" % self.provider)
        account_id = self.sms_twilio_account_id
        account_token = self.sms_twilio_token_id
        account_from = self.sms_twilio_from
        client = Client(account_id, account_token)
        result = []
        for message in messages:
            content = message["content"]
            numbers = message["numbers"]
            for number in numbers:
                state = "error"
                send_message = None
                try:
                    send_message = client.messages.create(
                        to=number["number"],
                        from_=account_from,
                        body=content,
                    )
                    _logger.info("Twilio SNS: %s" % send_message)
                    state = "success"
                except TwilioRestException as e:
                    _logger.error("Twilio SNS: %s" % e)
                    state = TWILIO_ERROR_STATES.get(e.code, "error")
                result.append({"state": state, "credit": 0, "res_id": number["number"]})
        return result

    def sns_amazon_send_sms_batch(self, messages):
        _logger.info("SMS Provider: %s" % self.provider)
        result = []
        for message in messages:
            numbers = message["numbers"]
            for number in numbers:
                result.append({"state": "sns_amazon_error", "credit": 0, "res_id": number["number"]})
        return result

        # NOTE: using Amazon SNS will result in an error for now since boto3 is not
        # compatible with the latest version of urllib3

        # account_id = self.sns_amazon_key
        # account_secret = self.sns_amazon_secret
        # account_region = self.sns_amazon_region
        # sns_client = boto3.client(
        #     "sns",
        #     aws_access_key_id=sns_key,
        #     aws_secret_access_key=sns_secret,
        #     region_name=sns_region,
        # )

        # message = sns_client.publish(
        #     PhoneNumber=messages[0]["number"],
        #     Message=messages[0]["content"],
        # )
        # state = "error"
        # if message:
        #     state = "success"

        # _logger.info("Amazon SNS: %s" % message)
        # return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]
