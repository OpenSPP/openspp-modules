# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


import ast
import json
import logging

from lxml import etree

from odoo import models

_logger = logging.getLogger(__name__)


class OpenSPPResPartner(models.Model):
    _inherit = "res.partner"

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
                action_id = action_id.context.replace("'", '"')
                is_group = ast.literal_eval(action_id).get("default_is_group")

                custom_page = etree.Element("page", {"string": "Additional Details"})
                indicators_page = etree.Element("page", {"string": "Indicators"})

                custom_div = etree.SubElement(custom_page, "div", {"class": "row mt16 o_settings_container"})
                indicators_div = etree.SubElement(indicators_page, "div", {"class": "row mt16 o_settings_container"})
                for rec in model_fields_id:
                    els = rec.name.split("_")
                    if len(els) >= 3 and (els[2] == "grp" and not is_group or els[2] == "indv" and is_group):
                        continue

                    if len(els) >= 2 and els[1] == "cst":
                        custom_div2 = etree.SubElement(
                            custom_div,
                            "div",
                            {"class": "col-12 col-lg-6 o_setting_box"},
                        )
                        custom_div_left = etree.SubElement(custom_div2, "div", {"class": "o_setting_left_pane"})
                        custom_div_right = etree.SubElement(custom_div2, "div", {"class": "o_setting_right_pane"})
                        if rec.ttype == "boolean":
                            etree.SubElement(custom_div_left, "field", {"name": rec.name})
                            etree.SubElement(custom_div_right, "label", {"for": rec.name})
                            if rec.help:
                                custom_div_right_help = etree.SubElement(
                                    custom_div_right, "div", {"class": "text-muted"}
                                )
                                span = etree.SubElement(custom_div_right_help, "span")
                                span.text = rec.help

                        else:
                            etree.SubElement(custom_div_right, "label", {"for": rec.name})

                            if rec.help:
                                custom_div_right_help = etree.SubElement(
                                    custom_div_right, "div", {"class": "text-muted"}
                                )
                                span = etree.SubElement(custom_div_right_help, "span")
                                span.text = rec.help

                            custom_div_right_inner_div = etree.SubElement(
                                custom_div_right, "div", {"class": "text-muted"}
                            )
                            etree.SubElement(custom_div_right_inner_div, "field", {"name": rec.name})

                    elif len(els) >= 2 and els[1] == "ind":
                        indicators_div2 = etree.SubElement(
                            indicators_div,
                            "div",
                            {"class": "col-12 col-lg-6 o_setting_box"},
                        )
                        indicators_div_left = etree.SubElement(indicators_div2, "div", {"class": "o_setting_left_pane"})
                        indicators_div_right = etree.SubElement(
                            indicators_div2, "div", {"class": "o_setting_right_pane"}
                        )
                        if rec.ttype == "boolean":
                            new_field = etree.SubElement(
                                indicators_div_left,
                                "field",
                                {
                                    "name": rec.name,
                                    "readonly": "1",
                                    "class": "oe_read_only",
                                },
                            )
                            etree.SubElement(indicators_div_right, "label", {"for": rec.name})
                            if rec.help:
                                indicators_div_right_help = etree.SubElement(
                                    indicators_div_right, "div", {"class": "text-muted"}
                                )
                                span = etree.SubElement(indicators_div_right_help, "span")
                                span.text = rec.help
                        else:
                            etree.SubElement(indicators_div_right, "label", {"for": rec.name})
                            if rec.help:
                                indicators_div_right_help = etree.SubElement(
                                    indicators_div_right, "div", {"class": "text-muted"}
                                )
                                span = etree.SubElement(indicators_div_right_help, "span")
                                span.text = rec.help
                            indicators_div_right_inner_div = etree.SubElement(
                                indicators_div_right, "div", {"class": "text-muted"}
                            )
                            new_field = etree.SubElement(
                                indicators_div_right_inner_div,
                                "field",
                                {"name": rec.name},
                            )

                        new_field.set("readonly", "1")
                        modifiers = {"readonly": True}
                        new_field.set("modifiers", json.dumps(modifiers))

                if custom_div.getchildren():
                    basic_info_page[0].addnext(custom_page)
                if indicators_div.getchildren():
                    basic_info_page[0].addnext(indicators_page)

                arch = doc
        return arch, view
