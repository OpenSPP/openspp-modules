# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPRegistrant(models.Model):
    _name = "res.partner"
    _inherit = [_name, "mail.thread"]

    id_pdf = fields.Binary("ID PASS")
    id_pdf_filename = fields.Char("ID File Name")
    image_1920_filename = fields.Char("Image 1920 FileName")
    pds_number = fields.Char(
        string="PDS Number", compute="_compute_pds_number", store=True
    )
    with_pds = fields.Boolean(default=False, compute="_compute_with_pds", store=True)

    @api.depends("reg_ids")
    def _compute_pds_number(self):
        for rec in self:
            rec.pds_number = ""
            for ids in rec.reg_ids:
                if ids.id_type.id == self.env.ref("spp_idpass.id_type_pds_number").id:
                    rec.pds_number = ids.value

    @api.depends("pds_number")
    def _compute_with_pds(self):
        for rec in self:
            rec.with_pds = False
            if rec.pds_number:
                rec.with_pds = True

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
        is_pds = False
        if id_pass_param:
            given_name = self.given_name
            identification_no = f"{self.id:06d}"

            if vals["pds_number"]:
                identification_no = vals["pds_number"]
                is_pds = True
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
                    if not vals["pds_number"]:
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

                idqueue = self.env["spp.id.queue"].search(
                    [("id", "=", vals["id_queue"])]
                )
                idqueue.id_pdf = self.id_pdf
                idqueue.id_pdf_filename = self.id_pdf_filename

                has_existing_idpass = self.env["g2p.reg.id"].search(
                    [
                        ("partner_id", "=", self.id),
                        ("id_type", "=", vals["id_type"]),
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
                                        "id_type": vals["id_type"],
                                        "value": identification_no,
                                        "is_pds": is_pds,
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
                                        "id_type": vals["id_type"],
                                        "value": identification_no,
                                        "is_pds": is_pds,
                                    },
                                )
                            ]
                        }
                    )
                return idqueue.id_pdf
            else:
                raise ValidationError(
                    _("ID PASS Error: %(reason)s Code: %(code)s")
                    % (response.reason, response.status_code)
                )  # noqa: C901
            _logger.info(
                "ID PASS Response: %s Code: %s"
                % (response.reason, response.status_code)
            )
            return
        else:
            raise ValidationError(_("ID Pass Error: No API set"))  # noqa: C901
