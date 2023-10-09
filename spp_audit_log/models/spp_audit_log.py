from dateutil import tz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval, datetime


class SppAuditLog(models.Model):
    _name = 'spp.audit.log'
    _description = 'SPP Audit Log'
    _order = 'create_date desc, id desc'

    audit_rule_id = fields.Many2one('spp.audit.rule', required=True)
    name = fields.Char('Resource Name', size=256, compute='_compute_name')
    create_date = fields.Datetime('Date', readonly=True)
    user_id = fields.Many2one('res.users', 'User', required=True, readonly=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True, readonly=True, ondelete='cascade')
    model = fields.Char(related='model_id.model')
    res_id = fields.Integer('Resource Id', readonly=True)
    method = fields.Char(size=64, readonly=True)
    data = fields.Text(readonly=True)
    data_html = fields.Html('HTML Data', readonly=True, compute='_compute_data_html')
    
    # Parent model based on audit rule
    parent_model_id = fields.Many2one('ir.model', 'Model', readonly=True, ondelete='cascade')
    parent_res_ids_str = fields.Text(readonly=True)
    
    # Where to log
    log_to = fields.Text(compute='_compute_log_to')
    
    @api.depends('parent_model_id')
    def _compute_log_to(self):
        for rec in self:
            if rec.parent_model_id:
                rec.log_to = f"{rec.parent_model_id.model}({rec.parent_res_ids_str})"
            else:
                rec.log_to = f"{rec.model_id.model}({rec.res_id})"

    def _compute_name(self):
        for rec in self:
            if rec.model_id and rec.res_id:
                record = rec.env[rec.model_id.model].browse(
                    rec.res_id).exists()
                if record:
                    rec.name = record.display_name
                else:
                    data = safe_eval(rec.data or '{}', {'datetime': datetime})
                    rec_name = rec.env[rec.model_id.model]._rec_name
                    if rec_name in data['new']:
                        rec.name = data['new'][rec_name]
                    elif rec_name in data['old']:
                        rec.name = data['old'][rec_name]
                    else:
                        rec.name = 'id=%s' % rec.res_id
            else:
                rec.name = ''

    def _format_value(self, field, value):
        self.ensure_one()
        if not value and field.type not in ('boolean', 'integer', 'float'):
            return ''
        if field.type == 'selection':
            selection = field.selection
            if callable(selection):
                selection = selection(self.env[self.model_id.model])
            return dict(selection).get(value, value)
        if field.type == 'many2one' and value:
            return self.env[field.comodel_name].browse(value). \
                exists().display_name or value
        if field.type == 'reference' and value:
            res_model, res_id = value.split(',')
            return self.env[res_model].browse(int(res_id)).exists(). \
                display_name or value
        if field.type in ('one2many', 'many2many') and value:
            return ', '.join([self.env[field.comodel_name].browse(rec_id).
                              exists().display_name or str(rec_id)
                              for rec_id in value])
        if field.type == 'binary' and value:
            return '&lt;binary data&gt;'
        if field.type == 'datetime':
            from_tz = tz.tzutc()
            to_tz = tz.gettz(self.env.user.tz)
            datetime_wo_tz = value
            datetime_with_tz = datetime_wo_tz.replace(tzinfo=from_tz)
            return fields.Datetime.to_string(
                datetime_with_tz.astimezone(to_tz))
        return value

    def _get_content(self):
        self.ensure_one()
        content = []
        data = safe_eval(self.data or '{}', {'datetime': datetime})
        RecordModel = self.env[self.model_id.model]
        for fname in set(data['new'].keys()) | set(data['old'].keys()):
            field = RecordModel._fields.get(fname)
            if field and (not field.groups or self.user_has_groups(
                    groups=field.groups)):
                old_value = self._format_value(
                    field, data['old'].get(fname, ''))
                new_value = self._format_value(
                    field, data['new'].get(fname, ''))
                if old_value != new_value:
                    label = field.get_description(self.env)['string']
                    content.append((label, old_value, new_value))
        return content

    def _compute_data_html(self):
        for rec in self:
            thead = ''
            for head in (_('Field'), _('Old value'), _('New value')):
                thead += '<th>%s</th>' % head
            thead = '<thead><tr>%s</tr></thead>' % thead
            tbody = ''
            for line in rec._get_content():
                row = ''
                for item in line:
                    row += '<td>%s</td>' % item
                tbody += '<tr>%s</tr>' % row
            tbody = '<tbody>%s</tbody>' % tbody
            rec.data_html = \
                '<table class="o_list_view table table-condensed ' \
                'table-striped">%s%s</table>' % (thead, tbody)
