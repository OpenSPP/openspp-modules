from odoo import models


class CustomDefaultCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def on_start_date_change(self, cycle):
        pass

    def mark_prepare_entitlement_as_done(self, cycle, msg):
        super().mark_prepare_entitlement_as_done()
        # Update Statistics
        cycle._compute_inkind_entitlements_count()
        return
