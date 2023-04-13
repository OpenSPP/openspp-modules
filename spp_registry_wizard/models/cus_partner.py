# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


import json
import logging

from lxml import etree

from odoo import _, models

_logger = logging.getLogger(__name__)


class OpenSPPResPartner(models.Model):
    _inherit = "res.partner"

    def open_create_member_wiz(self):
        """
        This opens the Member Creation Wizard
        """
        view = self.env.ref("spp_registry_wizard.create_member_wizard_form_view")
        wiz = self.env["spp.create.member.wizard"].create({"group_id": self.id})
        return {
            "name": _("Create Member"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "spp.create.member.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }
