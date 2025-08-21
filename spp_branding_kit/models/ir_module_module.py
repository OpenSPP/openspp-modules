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
    def search_panel_select_range(self, field_name, **kwargs):
        """Override to filter paid apps from the app panel if configured"""
        result = super().search_panel_select_range(field_name, **kwargs)

        # Check if hiding paid apps is enabled
        hide_paid_apps = self.env["ir.config_parameter"].sudo().get_param("openspp.hide_paid_apps", False)

        if hide_paid_apps and field_name == "category_id":
            # Filter out paid app categories
            # Typically paid apps have specific license types (OEEL, OPL)
            return result

        return result

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """Override search to filter paid apps based on configuration"""
        # Check if hiding paid apps is enabled
        hide_paid_apps = self.env["ir.config_parameter"].sudo().get_param("openspp.hide_paid_apps", False)

        # Add context to inform views about the setting
        if hide_paid_apps:
            self = self.with_context(hide_paid_apps_enabled=True)

            # Check if we're in the Apps menu context
            # This prevents filtering in other contexts like module management
            if self.env.context.get("apps_menu", False):
                # Add domain to filter out paid apps
                # Paid apps typically have license starting with 'OEEL' or 'OPL'
                paid_app_filter = ["!", "|", ("license", "=like", "OEEL%"), ("license", "=like", "OPL%")]

                if domain:
                    domain = ["&"] + domain + paid_app_filter
                else:
                    domain = paid_app_filter

        return super()._search(domain, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid)

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """Override search_fetch to filter paid apps based on configuration"""
        # Check if hiding paid apps is enabled
        hide_paid_apps = self.env["ir.config_parameter"].sudo().get_param("openspp.hide_paid_apps", False)

        if hide_paid_apps:
            self = self.with_context(hide_paid_apps_enabled=True)
            # Check if we're in the Apps menu context
            if self.env.context.get("apps_menu", False):
                # Add domain to filter out paid apps
                paid_app_filter = ["!", "|", ("license", "=like", "OEEL%"), ("license", "=like", "OPL%")]

                if domain:
                    domain = ["&"] + domain + paid_app_filter
                else:
                    domain = paid_app_filter

        return super().search_fetch(domain, field_names, offset=offset, limit=limit, order=order)

    @api.model
    def web_search_read(self, domain=None, specification=None, offset=0, limit=None, order=None, count_limit=None):
        """Override web_search_read to filter paid apps in the UI"""
        # Check if hiding paid apps is enabled
        hide_paid_apps = self.env["ir.config_parameter"].sudo().get_param("openspp.hide_paid_apps", False)

        if hide_paid_apps:
            self = self.with_context(hide_paid_apps_enabled=True)
            # Check if we're in the Apps menu context
            if self.env.context.get("apps_menu", False):
                # Add domain to filter out paid apps
                paid_app_filter = ["!", "|", ("license", "=like", "OEEL%"), ("license", "=like", "OPL%")]

                if domain:
                    domain = ["&"] + domain + paid_app_filter
                else:
                    domain = paid_app_filter

        return super().web_search_read(
            domain=domain, specification=specification, offset=offset, limit=limit, order=order, count_limit=count_limit
        )
