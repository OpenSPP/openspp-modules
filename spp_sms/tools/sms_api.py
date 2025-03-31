import logging

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from odoo import _

from odoo.addons.sms.tools.sms_api import SmsApi

# NOTE: Removing boto3 import as it is not compatible with the current version of urllib3
# import boto3

_logger = logging.getLogger(__name__)

original_send_sms_batch = SmsApi._send_sms_batch
original_get_sms_api_error_messages = SmsApi._get_sms_api_error_messages


def _send_sms_batch(self, messages, delivery_reports_url=False):
    account = self.env["iap.account"].search([("active_status", "=", True)]).get("sms")

    if not account:
        return

    _logger.info("SMS Provider: %s" % account[0].provider)

    if account[0].provider != "sms_twilio":
        return

    account_id = account[0].sms_twilio_account_id
    account_token = account[0].sms_twilio_token_id
    account_from = account[0].sms_twilio_from
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
                TWILIO_ERROR_STATES = {
                    21211: "invalid_to_number",
                    21212: "invalid_from_number",
                    21214: "cannot_be_reached",
                    63038: "reached_rate_limit",
                    21659: "invalid_from_number_mismatch",
                    21267: "invalid_from_number_alphanumeric",
                }

                state = TWILIO_ERROR_STATES.get(e.code, "error")
            result.append({"state": state, "credit": 0, "res_id": number["number"]})
    return result

    # NOTE: Removing sns_amazon for now since boto3 is not compatible with the current version of urllib3
    # elif account[0].provider == "sns_amazon":
    #     sns_key = account[0].sns_amazon_key
    #     sns_secret = account[0].sns_amazon_secret
    #     sns_region = account[0].sns_amazon_region
    #     sns_client = boto3.client(
    #         "sns",
    #         aws_access_key_id=sns_key,
    #         aws_secret_access_key=sns_secret,
    #         region_name=sns_region,
    #     )

    #     message = sns_client.publish(
    #         PhoneNumber=messages[0]["number"],
    #         Message=messages[0]["content"],
    #     )
    #     state = "error"
    #     if message:
    #         state = "success"

    #     _logger.info("Amazon SNS: %s" % message)
    #     return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]

    return original_send_sms_batch(self, messages, delivery_reports_url)


def _get_sms_api_error_messages(self):
    error_messages = original_get_sms_api_error_messages(self)
    error_messages["invalid_to_number"] = _(
        "The number you're trying to reach is not correctly formatted."
    )
    error_messages["invalid_from_number"] = _(
        "The number you're trying to send from is not correctly formatted."
    )
    error_messages["cannot_be_reached"] = _(
        "The number you're trying to reach is not correctly formatted."
    )
    error_messages["reached_rate_limit"] = _(
        "The number you're trying to reach has reached the rate limit."
    )
    error_messages["invalid_from_number_mismatch"] = _(
        "'From' number is not a Twilio phone number or Short Code country mismatch"
    )
    error_messages["invalid_from_number_alphanumeric"] = _(
        "Alphanumeric Sender ID cannot be used as the 'From' number"
    )
    return error_messages


# # Monkey patch the original class
SmsApi._send_sms_batch = _send_sms_batch
SmsApi._get_sms_api_error_messages = _get_sms_api_error_messages
