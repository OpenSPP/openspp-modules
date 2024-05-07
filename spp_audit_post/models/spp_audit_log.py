from odoo import _, api, fields, models
from odoo.tools.safe_eval import datetime, safe_eval


class SppAuditLog(models.Model):
    _inherit = "spp.audit.log"

    parent_data_html = fields.Html("Parent HTML Data", readonly=True, compute="_compute_parent_data_html")

    # Parent model based on audit rule
    parent_model_id = fields.Many2one("ir.model", "Parent Model", readonly=True, ondelete="cascade")
    parent_res_ids_str = fields.Text(readonly=True)

    # Where to log
    log_to = fields.Text(compute="_compute_log_to")

    @api.model
    def create(self, vals):
        res = super().create(vals)

        records = []
        msg = ""
        if res.parent_model_id and res.parent_model_id.is_mail_thread:
            res_ids = list(map(int, res.parent_res_ids_str.split(",")))
            records = self.env[res.parent_model_id.model].browse(res_ids)
            msg = res.parent_data_html
        elif res.model_id and res.model_id.is_mail_thread:
            records = self.env[res.model_id.model].browse(res.res_id)
            msg = res.data_html

        for record in records:
            record.message_post(body=msg)

        return res

    def _parent_get_content(self):
        """
        The function `_parent_get_content` retrieves the content of a record and compares the old and
        new values of its fields, returning a list of tuples containing the record name, field label,
        old value, and new value for each field that has changed.
        :return: a list of tuples containing information about the changes made to a record. Each tuple
        in the list represents a change and contains the following elements:
        """
        self.ensure_one()
        content = []
        data = safe_eval(self.data or "{}", {"datetime": datetime})
        RecordModel = self.env[self.model_id.model]
        record = RecordModel.browse(self.res_id)
        if record and hasattr(record, "name"):
            record_name = record.name
        else:
            record_name = self.model_id.name
        for fname in set(data["new"].keys()) | set(data["old"].keys()):
            field = RecordModel._fields.get(fname)
            if field and (not field.groups or self.user_has_groups(groups=field.groups)):
                old_value = self._format_value(field, data["old"].get(fname, ""))
                new_value = self._format_value(field, data["new"].get(fname, ""))
                if old_value != new_value:
                    label = field.get_description(self.env)["string"]
                    content.append((record_name, label, old_value, new_value))
        return content

    def _compute_parent_data_html(self):
        for rec in self:
            thead = ""
            for head in (_("Model"), _("Field"), _("Old value"), _("New value")):
                thead += f"<th>{head}</th>"
            thead = "<thead><tr>%s</tr></thead>" % thead
            tbody = ""
            for line in rec._parent_get_content():
                row = ""
                for item in line:
                    row += "<td>%s</td>" % item
                tbody += "<tr>%s</tr>" % row
            tbody = "<tbody>%s</tbody>" % tbody
            rec.parent_data_html = (
                '<table class="o_list_view table table-condensed ' f'table-striped">{thead}{tbody}</table>'
            )

    @api.depends("parent_model_id")
    def _compute_log_to(self):
        for rec in self:
            if rec.parent_model_id:
                rec.log_to = f"{rec.parent_model_id.model}({rec.parent_res_ids_str})"
            else:
                rec.log_to = f"{rec.model_id.model}({rec.res_id})"
