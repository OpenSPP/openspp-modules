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

    def _group_fields_by_group(self, fields_list):
        """
        Group fields by their field_group_id and sort by sequence.
        Returns a list of tuples (group_record, fields_in_group).
        Fields without a group are returned with group_record=None.
        """
        from collections import defaultdict

        grouped = defaultdict(list)

        # Check if field_group_id exists on the model
        has_group_field = hasattr(fields_list[0], "field_group_id") if fields_list else False
        has_sequence_field = hasattr(fields_list[0], "sequence") if fields_list else False

        for field in fields_list:
            group_id = None
            if has_group_field and field.field_group_id:
                group_id = field.field_group_id.id
            grouped[group_id].append(field)

        # Sort fields within each group by sequence
        for group_id in grouped:
            if has_sequence_field:
                grouped[group_id] = sorted(grouped[group_id], key=lambda f: (f.sequence, f.field_description))
            else:
                grouped[group_id] = sorted(grouped[group_id], key=lambda f: f.field_description)

        # Get group records and sort groups by sequence
        result = []
        group_ids = [gid for gid in grouped.keys() if gid is not None]
        if group_ids and "spp.custom.field.group" in self.env:
            try:
                group_records = self.env["spp.custom.field.group"].browse(group_ids)
                group_records = group_records.sorted(key=lambda g: g.sequence)
                for group in group_records:
                    result.append((group, grouped[group.id]))
            except KeyError:
                # Model doesn't exist, treat all fields as ungrouped
                _logger.warning("spp.custom.field.group model not found, ignoring field groups")
                if None in grouped:
                    result.append((None, grouped[None]))

        # Add fields without a group at the end
        if None in grouped:
            result.append((None, grouped[None]))

        return result

    def _get_view(self, view_id=None, view_type="form", **options):  # noqa: C901
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
                order="sequence, ttype, field_description",
            )
            if basic_info_page:
                if action_id.context:
                    action_id = action_id.context.replace("'", '"')
                is_group = ast.literal_eval(action_id).get("default_is_group")

                custom_page = etree.Element("page", {"string": "Additional Details", "name": "additional_details"})
                indicators_page = etree.Element("page", {"string": "Indicators", "name": "indicators"})

                # Separate custom and indicator fields
                custom_fields = []
                indicator_fields = []

                for rec in model_fields_id:
                    els = rec.name.split("_")
                    if len(els) >= 3 and (els[2] == "grp" and not is_group or els[2] == "indv" and is_group):
                        continue

                    if len(els) >= 2 and els[1] == "cst":
                        custom_fields.append(rec)
                    elif len(els) >= 2 and els[1] == "ind":
                        indicator_fields.append(rec)

                # Process custom fields with grouping
                if custom_fields:
                    grouped_custom_fields = self._group_fields_by_group(custom_fields)

                    # Create main container row for side-by-side layout
                    main_row = etree.SubElement(custom_page, "div", {"class": "row"})

                    for group_record, fields_in_group in grouped_custom_fields:
                        if group_record:
                            # Create a half-width column for each group
                            group_col = etree.SubElement(
                                main_row,
                                "div",
                                {"class": "col-12 col-lg-6"},
                            )
                            # Add group label/title
                            group_label_div = etree.SubElement(
                                group_col,
                                "div",
                                {"class": "o_horizontal_separator mt-2 mb-3"},
                            )
                            group_label = etree.SubElement(
                                group_label_div,
                                "strong",
                            )
                            group_label.text = group_record.name
                            # Create fields container
                            group_div = etree.SubElement(group_col, "div", {"class": "row mt16 o_settings_container"})
                            for field in fields_in_group:
                                self.create_field_element(group_div, field)
                        else:
                            # Fields without a group go in full width at the bottom
                            if not custom_page.xpath(".//div[@class='row mt16 o_settings_container o_no_group']"):
                                custom_div = etree.SubElement(
                                    custom_page, "div", {"class": "row mt16 o_settings_container o_no_group"}
                                )
                            else:
                                custom_div = custom_page.xpath(
                                    ".//div[@class='row mt16 o_settings_container o_no_group']"
                                )[0]
                            for field in fields_in_group:
                                self.create_field_element(custom_div, field)

                # Process indicator fields with grouping
                if indicator_fields:
                    grouped_indicator_fields = self._group_fields_by_group(indicator_fields)

                    # Create main container row for side-by-side layout
                    main_row = etree.SubElement(indicators_page, "div", {"class": "row"})

                    for group_record, fields_in_group in grouped_indicator_fields:
                        if group_record:
                            # Create a half-width column for each group
                            group_col = etree.SubElement(
                                main_row,
                                "div",
                                {"class": "col-12 col-lg-6"},
                            )
                            # Add group label/title
                            group_label_div = etree.SubElement(
                                group_col,
                                "div",
                                {"class": "o_horizontal_separator mt-2 mb-3"},
                            )
                            group_label = etree.SubElement(
                                group_label_div,
                                "strong",
                            )
                            group_label.text = group_record.name
                            # Create fields container
                            group_div = etree.SubElement(group_col, "div", {"class": "row mt16 o_settings_container"})
                            for field in fields_in_group:
                                self.create_field_element(group_div, field, is_ind=True)
                        else:
                            # Fields without a group go in full width at the bottom
                            if not indicators_page.xpath(".//div[@class='row mt16 o_settings_container o_no_group']"):
                                indicators_div = etree.SubElement(
                                    indicators_page, "div", {"class": "row mt16 o_settings_container o_no_group"}
                                )
                            else:
                                indicators_div = indicators_page.xpath(
                                    ".//div[@class='row mt16 o_settings_container o_no_group']"
                                )[0]
                            for field in fields_in_group:
                                self.create_field_element(indicators_div, field, is_ind=True)

                if custom_page.getchildren():
                    basic_info_page[0].addnext(custom_page)
                if indicators_page.getchildren():
                    basic_info_page[0].addnext(indicators_page)

                arch = doc
        return arch, view
