import logging

from odoo import _

from odoo.addons.sms.tools.sms_api import SmsApi

# NOTE: Removing boto3 import as it is not compatible with the current version of urllib3
# import boto3

_logger = logging.getLogger(__name__)

original_send_sms_batch = SmsApi._send_sms_batch
original_get_sms_api_error_messages = SmsApi._get_sms_api_error_messages


def _send_sms_batch(self, messages, delivery_reports_url=False):
    account = self.env["iap.account"].search(
        [("active_status", "=", True), ("service_name", "=", "sms")], order="sequence", limit=1
    )

    if not account or account.provider not in ["sms_twilio", "sns_amazon"]:
        return original_send_sms_batch(self, messages, delivery_reports_url)

    elif account.provider == "sms_twilio":
        return account.twilio_send_sms_batch(messages)
    elif account.provider == "sns_amazon":
        return account.sns_amazon_send_sms_batch(messages)


def _get_sms_api_error_messages(self):
    error_messages = original_get_sms_api_error_messages(self)
    error_messages["invalid_to_number"] = _("The number cannot be reached. Please check the number.")
    error_messages["invalid_from_number"] = _("The number you're trying to use is not correctly formatted.")
    error_messages["cannot_be_reached"] = _("The number cannot be reached. Please check the number.")
    error_messages["reached_rate_limit"] = _("The number you're trying to reach has reached the rate limit.")
    error_messages["invalid_from_number_mismatch"] = _(
        "'From' number is not a Twilio phone number or Short Code country mismatch"
    )
    error_messages["invalid_from_number_alphanumeric"] = _("Alphanumeric Sender ID cannot be used as the 'From' number")
    error_messages["sns_amazon_error"] = _("Amazon SNS is not yet supported.")
    return error_messages


# # Monkey patch the original class
SmsApi._send_sms_batch = _send_sms_batch
SmsApi._get_sms_api_error_messages = _get_sms_api_error_messages
