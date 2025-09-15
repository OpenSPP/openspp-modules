from odoo import api, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def get_paid_apps_count(self):
        """Get count of paid apps in the system"""
        paid_apps = self.search(["|", ("license", "=like", "OEEL%"), ("license", "=like", "OPL%")])
        return len(paid_apps)

    # No overrides of install/upgrade/uninstall buttons are needed once
    # _search is left untouched; UI filtering is handled via web_* APIs.
