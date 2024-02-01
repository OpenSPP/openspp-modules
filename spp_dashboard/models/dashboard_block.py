# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging
from ast import literal_eval

from odoo import fields, models
from odoo.osv import expression
from odoo.tools import safe_eval

_logger = logging.getLogger(__name__)


class DashBoardBlock(models.Model):
    _inherit = "dashboard.block"

    use_func = fields.Boolean("Use Function")
    func = fields.Char("Function")
    args = fields.Char("Arguments")
    result_type = fields.Selection(
        selection=[("int", "Integer"), ("float", "Float")],
        string="Result Data Type",
        default="int",
    )

    def get_dashboard_vals(self, action_id, active_id):
        """Dashboard block values"""
        block_id = []
        dashboard_block = self.env["dashboard.block"].sudo().search([("client_action", "=", int(action_id))])
        for rec in dashboard_block:
            color = rec.tile_color if rec.tile_color else "#1f6abb;"
            icon_color = rec.fa_color if rec.fa_color else "#1f6abb;"
            text_color = rec.text_color if rec.text_color else "#FFFFFF;"
            vals = {
                "id": rec.id,
                "name": rec.name,
                "type": rec.type,
                "graph_type": rec.graph_type,
                "icon": rec.fa_icon,
                "cols": rec.graph_size,
                "color": "background-color: %s;" % color,
                "text_color": "color: %s;" % text_color,
                "icon_color": "color: %s;" % icon_color,
            }
            domain = []
            if rec.filter and not rec.use_func:
                domain = self.check_filter(rec.filter, active_id)

            if rec.model_name:
                if rec.type == "graph":
                    records = self.get_records(
                        rec.model_name,
                        domain,
                        rec.operation,
                        rec.measured_field,
                        rec.group_by,
                    )

                    x_axis = []
                    for record in records:
                        x_axis.append(record.get(rec.group_by.name))
                    y_axis = []
                    for record in records:
                        y_axis.append(record.get("value"))
                    vals.update({"x_axis": x_axis, "y_axis": y_axis})
                else:
                    if not rec.use_func:
                        records = self.get_records(rec.model_name, domain, rec.operation, rec.measured_field)
                        if records:
                            val = self.format_totals(records[0].get("value"), rec.result_type or "int")
                            records[0]["value"] = val
                            vals.update(records[0])
                    else:  # Get value from function
                        model_func_args = "self.env['" + rec.model_name + "']." + rec.func + "(" + rec.args + ")"
                        try:
                            records = safe_eval.safe_eval(model_func_args, {"self": self})
                        except Exception as ex:
                            _logger.info(
                                f"DEBUG! Error executing the function: {model_func_args} of model: {rec.model_name}"
                            )
                            _logger.info("DEBUG! %s " % ex)
                            records = None
                        if records:
                            val = self.format_totals(records.get("value"), rec.result_type or "int")
                            records["value"] = val
                            vals.update(records)

            block_id.append(vals)
        # _logger.info("Block_ID: %s" % block_id)
        return block_id

    def format_totals(self, total, result_type):
        if result_type == "int":
            # val = "{:,}".format(total)
            val = f"{total:,}"
        else:
            magnitude = 0
            while abs(total) >= 1000:
                magnitude += 1
                total /= 1000.0
            # add more suffixes if you need them
            val = "{:.2f}{}".format(
                total,
                ["", "K", "M", "G", "T", "P"][magnitude],
            )
        return val

    def get_records(self, model_name, domain, operation, measured_field, group_by=None):
        try:
            query = self.env[model_name].get_query(
                domain,
                operation,
                measured_field,
                group_by=group_by,
            )
            self._cr.execute(query)
            records = self._cr.dictfetchall()
        except Exception:
            records = []
        _logger.info("Query: %s" % query)
        # _logger.info("Records: %s" %records)
        return records

    def check_filter(self, ftr, active_id):
        if ftr:
            domain = expression.AND([literal_eval(ftr)])
            idx1 = 0
            for dom in domain:
                if type(dom) in (list, tuple):
                    if type(dom) == tuple:
                        dom = list(dom)
                    try:
                        idx2 = dom.index("active_id")
                    except Exception:
                        # _logger.info("DEBUG! Exception: %s", ex)
                        idx2 = None
                    if idx2:
                        # _logger.info("DEBUG! context: %s", self.env.context)
                        dom[idx2] = active_id
                    domain[idx1] = tuple(dom)
                idx1 += 1
            _logger.info("DEBUG! domain: %s", domain)
            return domain
        else:
            return ftr
