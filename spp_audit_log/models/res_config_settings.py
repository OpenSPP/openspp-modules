from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    audit_log_to_file = fields.Boolean(
        string="Enable File Logging",
        config_parameter="spp.audit_log_to_file",
        help="Enable logging audit records to JSON file instead of database",
    )

    audit_log_file_path = fields.Char(
        string="Audit Log File Path",
        default="/var/log/odoo/audit.log",
        config_parameter="spp.audit_log_file_path",
        help="Full path to the audit log file (JSON Lines format)",
    )

    audit_log_file_max_bytes = fields.Integer(
        string="Max File Size (MB)",
        default=10,
        config_parameter="spp.audit_log_file_max_bytes",
        help="Maximum size of log file in megabytes before rotation",
    )

    audit_log_file_backup_count = fields.Integer(
        string="Backup Count",
        default=5,
        config_parameter="spp.audit_log_file_backup_count",
        help="Number of backup files to keep during rotation",
    )
