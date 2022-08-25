# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPRegistrant(models.Model):
    _name = "res.partner"
    _inherit = [_name, "mail.thread"]

    id_pdf = fields.Binary("ID PASS")
    id_pdf_filename = fields.Char("ID File Name")
    image_1920_filename = fields.Char("Image 1920 FileName")

    def open_issue_idpass_wiz(self):
        view = self.env.ref("spp_idpass.issue_id_pass_wizard_form_view")
        wiz = self.env["spp.issue.idpass.wizard"].create({"registrant_id": self.id})
        return {
            "name": _("Issue ID Pass"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "spp.issue.idpass.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }

    def send_idpass_parameters(self, vals):  # noqa: C901
        id_pass_param = self.env["spp.id.pass"].search([("is_active", "=", True)])
        if vals["idpass"]:
            id_pass_param = self.env["spp.id.pass"].search(
                [("id", "=", vals["idpass"])]
            )

        if id_pass_param:

            given_name = self.given_name
            identification_no = f"{self.id:06d}"
            birth_place = self.birth_place or ""
            gender = self.gender or ""
            surname = self.family_name
            profile_pic = self.image_1920 or False
            profile_pic_filename = self.image_1920_filename or False
            if self.is_group:
                head_id = 0
                for group_member in self.group_membership_ids:
                    for member_kind in group_member.kind:
                        if member_kind.is_unique:
                            head_id = group_member.individual.id
                            break
                    if head_id > 0:
                        break
                if head_id > 0:
                    head_registrant = self.env["res.partner"].search(
                        [("id", "=", head_id)]
                    )
                    given_name = head_registrant.given_name
                    identification_no = f"{head_registrant.id:09d}"
                    birth_place = head_registrant.birth_place or ""
                    gender = head_registrant.gender or ""
                    surname = head_registrant.family_name
                    profile_pic = head_registrant.image_1920 or False
                    profile_pic_filename = head_registrant.image_1920_filename or False
                else:
                    raise ValidationError(
                        _(
                            "ID PASS Error: No Head or Principal Recipient assigned to this Group"
                        )
                    )  # noqa: C901

            issue_date = datetime.today().strftime("%Y/%m/%d")

            expiry_date = datetime.today()

            if id_pass_param[0].expiry_length_type == "years":
                expiry_date = datetime.today() + relativedelta(
                    years=id_pass_param[0].expiry_length
                )
            elif id_pass_param[0].expiry_length_type == "months":
                expiry_date = datetime.today() + relativedelta(
                    months=id_pass_param[0].expiry_length
                )
            else:
                expiry_date = datetime.today() + relativedelta(
                    days=id_pass_param[0].expiry_length
                )
            expiry_date = expiry_date.strftime("%Y/%m/%d")

            file_type = ""
            if profile_pic_filename:

                file_type = profile_pic_filename.partition(".")[2]
                if file_type == "jpg":
                    file_type = "jpeg"
            else:
                if profile_pic:
                    raise ValidationError(
                        _("ID PASS Error: Please try reuploading the ID Picture")
                    )  # noqa: C901
            profile_pic_url = ""

            data = {
                "fields": {
                    "date_of_expiry": expiry_date,
                    "date_of_issue": issue_date,
                    "given_names": given_name,
                    "identification_no": identification_no,
                    "nationality": "Filipino",
                    "place_of_birth": birth_place,
                    "sex": gender,
                    "surname": surname,
                    "qrcode_svg_1": f"{identification_no};{given_name};{surname}",
                }
            }

            if profile_pic and file_type in ("jpeg", "png"):
                profile_pic = str(profile_pic)
                profile_pic = profile_pic[2:]
                profile_pic_url = "data:image/" + file_type + ";base64," + profile_pic

                data["fields"].update(
                    {
                        "profile_svg_6": profile_pic_url,
                    }
                )

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            response = requests.post(
                id_pass_param[0].api_url,
                data=json.dumps(data),
                headers=headers,
                auth=(id_pass_param[0].api_username, id_pass_param[0].api_password),
            )
            if response.status_code == 200:
                pdf_vals = response.json()
                file_pdf = pdf_vals["files"]["pdf"]
                file_pdf = file_pdf[28:]
                self.id_pdf = file_pdf
                self.id_pdf_filename = "{}_{}_{}.pdf".format(
                    id_pass_param[0].filename_prefix,
                    identification_no,
                    datetime.today().strftime("%Y-%m-%d"),
                )

                attachment = self.env["ir.attachment"].create(
                    {
                        "name": self.id_pdf_filename,
                        "type": "binary",
                        "datas": file_pdf,
                        "res_model": self._name,
                        "res_id": self.id,
                        "mimetype": "application/x-pdf",
                    }
                )

                # TODO: Add the identification_no to the ID of the registrant

                attachment_id = {attachment.id}
                model_id = self.env["res.partner"].search([("id", "=", self.id)])
                msg_body = "Generated ID: " + self.id_pdf_filename
                model_id.message_post(body=msg_body, attachment_ids=attachment_id)

                external_identifier = self.env["ir.model.data"].search(
                    [("name", "=", "id_type_idpass"), ("model", "=", "g2p.id.type")]
                )
                _logger.info("External Identifier: %s" % external_identifier.res_id)
                has_existing_idpass = self.env["g2p.reg.id"].search(
                    [
                        ("registrant", "=", self.id),
                        ("id_type", "=", external_identifier.res_id),
                    ]
                )
                if has_existing_idpass:
                    self.update(
                        {
                            "reg_ids": [
                                (
                                    1,
                                    has_existing_idpass[0].id,
                                    {
                                        "id_type": external_identifier.res_id,
                                        "value": identification_no,
                                    },
                                )
                            ]
                        }
                    )
                else:
                    self.write(
                        {
                            "reg_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "id_type": external_identifier.res_id,
                                        "value": identification_no,
                                    },
                                )
                            ]
                        }
                    )
                return {
                    "effect": {
                        "fadeout": "slow",
                        "message": "ID Pass has been generated!",
                        "type": "rainbow_man",
                    }
                }
            else:
                raise ValidationError(
                    _(
                        "ID PASS Error: %s Code: %s"
                        % (response.reason, response.status_code)
                    )
                )  # noqa: C901
            _logger.info(
                "ID PASS Response: %s Code: %s"
                % (response.reason, response.status_code)
            )
            return
        else:
            raise ValidationError(_("ID Pass Error: No API set"))  # noqa: C901
