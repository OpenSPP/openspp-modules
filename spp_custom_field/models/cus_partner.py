# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


import ast
import json
import logging

from lxml import etree

from odoo import models

_logger = logging.getLogger(__name__)


class OpenSPPResPartner(models.Model):
    _inherit = "res.partner"

    def create_field_element(self, div_element, model_field_id, is_ind=False):
        div_element2 = etree.SubElement(
            div_element,
            "div",
            {"class": "col-12 col-lg-6 o_setting_box"},
        )
        div_element_left = etree.SubElement(div_element2, "div", {"class": "o_setting_left_pane"})
        div_element_right = etree.SubElement(div_element2, "div", {"class": "o_setting_right_pane"})

        if model_field_id.ttype == "boolean":
            sub_element_params = {
                "name": model_field_id.name,
            }
            new_field = etree.SubElement(
                div_element_left,
                "field",
                sub_element_params,
            )
            etree.SubElement(div_element_right, "label", {"for": model_field_id.name})
            if model_field_id.help:
                div_element_right_help = etree.SubElement(div_element_right, "div", {"class": "text-muted"})
                span = etree.SubElement(div_element_right_help, "span")
                span.text = model_field_id.help

        else:
            etree.SubElement(div_element_right, "label", {"for": model_field_id.name})

            if model_field_id.help:
                div_element_right_help = etree.SubElement(div_element_right, "div", {"class": "text-muted"})
                span = etree.SubElement(div_element_right_help, "span")
                span.text = model_field_id.help

            div_element_right_inner_div = etree.SubElement(div_element_right, "div", {"class": "text-muted"})
            new_field = etree.SubElement(div_element_right_inner_div, "field", {"name": model_field_id.name})

        if is_ind:
            new_field.set("readonly", "1")
            modifiers = {"readonly": True}
            new_field.set("modifiers", json.dumps(modifiers))

    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type == "form":
            doc = arch
            basic_info_page = doc.xpath("//page[@name='basic_info']")

            action_id = self.env["ir.actions.act_window"].browse(options.get("action_id"))
            if not action_id:
                act_window_view = self.env["ir.actions.act_window.view"].search([("view_id", "=", view_id)], limit=1)
                action_id = act_window_view.act_window_id

            model_fields_id = self.env["ir.model.fields"].search(
                [("model_id", "=", "res.partner")],
                order="ttype, field_description",
            )
            if basic_info_page:
                if action_id.context:
                    action_id = action_id.context.replace("'", '"')
                is_group = ast.literal_eval(action_id).get("default_is_group")

                custom_page = etree.Element("page", {"string": "Additional Details", "name": "additional_details"})
                indicators_page = etree.Element("page", {"string": "Indicators", "name": "indicators"})

                custom_div = etree.SubElement(custom_page, "div", {"class": "row mt16 o_settings_container"})
                indicators_div = etree.SubElement(indicators_page, "div", {"class": "row mt16 o_settings_container"})
                for rec in model_fields_id:
                    els = rec.name.split("_")
                    if len(els) >= 3 and (els[2] == "grp" and not is_group or els[2] == "indv" and is_group):
                        continue

                    if len(els) >= 2 and els[1] == "cst":
                        self.create_field_element(custom_div, rec)

                    elif len(els) >= 2 and els[1] == "ind":
                        self.create_field_element(indicators_div, rec, is_ind=True)

                if custom_div.getchildren():
                    basic_info_page[0].addnext(custom_page)
                if indicators_div.getchildren():
                    basic_info_page[0].addnext(indicators_page)

                arch = doc
        return arch, view
