# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

import boto3
from twilio.rest import Client

from odoo import models

_logger = logging.getLogger(__name__)


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _check_sms(self, number, message, sms_id):
        return "success"

    def _send_sms_batch(self, messages):
        account = self.env["iap.account"].search([("active_status", "=", True)])
        if account:
            _logger.info("SMS Provider: %s" % account[0].provider)
            if account[0].provider == "sms_twilio":
                account_id = account[0].sms_twilio_account_id
                account_token = account[0].sms_twilio_token_id
                account_from = account[0].sms_twilio_from
                client = Client(account_id, account_token)
                message = client.messages.create(
                    to=messages[0]["number"],
                    from_=account_from,
                    body=messages[0]["content"],
                )
                state = "error"
                if message:
                    state = "success"
                _logger.info("Twilio SNS: %s" % message)
                return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]
            elif account[0].provider == "sns_amazon":
                sns_key = account[0].sns_amazon_key
                sns_secret = account[0].sns_amazon_secret
                sns_region = account[0].sns_amazon_region
                sns_client = boto3.client(
                    "sns",
                    aws_access_key_id=sns_key,
                    aws_secret_access_key=sns_secret,
                    region_name=sns_region,
                )

                message = sns_client.publish(
                    PhoneNumber=messages[0]["number"],
                    Message=messages[0]["content"],
                )
                state = "error"
                if message:
                    state = "success"

                _logger.info("Amazon SNS: %s" % message)
                return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]
        else:
            return super()._send_sms_batch(messages)
