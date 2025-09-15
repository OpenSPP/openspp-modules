# ABOUTME: Configuration settings for OpenSPP branding and telemetry
# ABOUTME: Provides centralized settings for debranding customization

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # OpenSPP Branding Settings
    openspp_system_name = fields.Char(
        "System Name",
        help="Set your organization's system name for the interface",
        default="OpenSPP Platform",
        config_parameter="openspp.system.name",
    )

    openspp_documentation_url = fields.Char(
        "Documentation URL",
        help="Documentation URL for your OpenSPP implementation",
        default="https://docs.openspp.org",
        config_parameter="openspp.documentation.url",
    )

    openspp_support_url = fields.Char(
        "Support URL",
        help="Support website for your OpenSPP users",
        default="https://openspp.org",
        config_parameter="openspp.support.url",
    )

    openspp_show_powered_by = fields.Boolean(
        "Display OpenSPP Branding",
        help="Display 'Powered by OpenSPP' branding",
        default=True,
        config_parameter="openspp.show.powered_by",
    )

    # Telemetry Settings
    openspp_telemetry_enabled = fields.Boolean(
        "Enable Telemetry",
        help="Share anonymous usage statistics to improve OpenSPP",
        default=True,
        config_parameter="openspp.telemetry.enabled",
    )

    openspp_telemetry_endpoint = fields.Char(
        "Telemetry Endpoint",
        help="Endpoint for usage statistics collection",
        default="https://telemetry.openspp.org",
        config_parameter="openspp.telemetry.endpoint",
    )

    openspp_hide_odoo_referral = fields.Boolean(
        "OpenSPP Interface Mode",
        help="Optimize interface for OpenSPP-specific workflows",
        default=True,
        config_parameter="openspp.ui.hide_odoo_referral",
    )

    openspp_hide_paid_apps = fields.Boolean(
        "Hide Paid Apps",
        help="Hide paid Odoo apps (Enterprise and OPL licensed modules) from the Apps list",
        default=True,
        config_parameter="openspp.hide_paid_apps",
    )

    openspp_default_app_filter = fields.Selection(
        [
            ("all", "All Modules"),
            ("apps_only", "Apps Only"),
            ("openspp", "OpenSPP Apps Only"),
            ("free", "Free Apps Only"),
        ],
        string="Default Apps Filter",
        help="Choose which modules to show by default in the Apps menu",
        default="apps_only",
        config_parameter="openspp.default_app_filter",
    )
