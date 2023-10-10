from odoo import _, api, fields, models
from odoo.tools.safe_eval import datetime, safe_eval


class SppAuditLog(models.Model):
    _inherit = "spp.audit.log"

    parent_data_html = fields.Html(
        "Parent HTML Data", readonly=True, compute="_compute_parent_data_html"
    )

    @api.model
    def create(self, vals):
        res = super(SppAuditLog, self).create(vals)

        if res.parent_model_id:
            res_ids = list(map(int, res.parent_res_ids_str.split(",")))
            records = self.env[res.parent_model_id.model].browse(res_ids)
            msg = res.parent_data_html
        else:
            records = self.env[res.model_id.model].browse(res.res_id)
            msg = res.data_html

        for record in records:
            record.message_post(body=msg)

        return res

    def _parent_get_content(self):
        self.ensure_one()
        content = []
        data = safe_eval(self.data or "{}", {"datetime": datetime})
        RecordModel = self.env[self.model_id.model]
        record = RecordModel.browse(self.res_id)
        record_name = ""
        if record:
            record_name = record.name
        for fname in set(data["new"].keys()) | set(data["old"].keys()):
            field = RecordModel._fields.get(fname)
            if field and (
                not field.groups or self.user_has_groups(groups=field.groups)
            ):
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
                thead += "<th>%s</th>" % head
            thead = "<thead><tr>%s</tr></thead>" % thead
            tbody = ""
            for line in rec._parent_get_content():
                row = ""
                for item in line:
                    row += "<td>%s</td>" % item
                tbody += "<tr>%s</tr>" % row
            tbody = "<tbody>%s</tbody>" % tbody
            rec.parent_data_html = (
                '<table class="o_list_view table table-condensed '
                'table-striped">%s%s</table>' % (thead, tbody)
            )
