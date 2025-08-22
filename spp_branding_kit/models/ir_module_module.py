# ABOUTME: Override ir.module.module to filter paid apps from the app list
# ABOUTME: Provides option to hide paid Odoo apps based on configuration

from odoo import api, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def get_paid_apps_count(self):
        """Get count of paid apps in the system"""
        paid_apps = self.search(["|", ("license", "=like", "OEEL%"), ("license", "=like", "OPL%")])
        return len(paid_apps)

    @api.model
    def _get_paid_app_filter(self):
        """Helper method to get the domain filter for paid apps"""
        return ["!", "|", ("license", "=like", "OEEL%"), ("license", "=like", "OPL%")]

    @api.model
    def _apply_paid_app_filter(self, domain):
        """Helper method to apply paid app filter to a domain"""
        hide_paid_apps = self.env["ir.config_parameter"].sudo().get_param("openspp.hide_paid_apps", False)

        if hide_paid_apps and self.env.context.get("apps_menu", False):
            paid_app_filter = self._get_paid_app_filter()
            if domain:
                return ["&"] + domain + paid_app_filter
            else:
                return paid_app_filter
        return domain

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """Override search to filter paid apps based on configuration"""
        # Apply paid app filter if needed
        domain = self._apply_paid_app_filter(domain)

        # Add context to inform views about the setting
        hide_paid_apps = self.env["ir.config_parameter"].sudo().get_param("openspp.hide_paid_apps", False)
        if hide_paid_apps:
            self = self.with_context(hide_paid_apps_enabled=True)

        return super()._search(domain, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid)

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """Override search_fetch to filter paid apps based on configuration"""
        # Apply paid app filter if needed
        domain = self._apply_paid_app_filter(domain)

        # Add context to inform views about the setting
        hide_paid_apps = self.env["ir.config_parameter"].sudo().get_param("openspp.hide_paid_apps", False)
        if hide_paid_apps:
            self = self.with_context(hide_paid_apps_enabled=True)

        return super().search_fetch(domain, field_names, offset=offset, limit=limit, order=order)

    @api.model
    def web_search_read(self, domain=None, specification=None, offset=0, limit=None, order=None, count_limit=None):
        """Override web_search_read to filter paid apps in the UI"""
        # Apply paid app filter if needed
        domain = self._apply_paid_app_filter(domain)

        # Add context to inform views about the setting
        hide_paid_apps = self.env["ir.config_parameter"].sudo().get_param("openspp.hide_paid_apps", False)
        if hide_paid_apps:
            self = self.with_context(hide_paid_apps_enabled=True)

        return super().web_search_read(
            domain=domain, specification=specification, offset=offset, limit=limit, order=order, count_limit=count_limit
        )
