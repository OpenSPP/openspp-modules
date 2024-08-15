from unittest.mock import patch

from .common import Common


class CashEntitlementManagerTest(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cash_entitlement_manager = cls.env["g2p.program.entitlement.manager.cash"].create(
            {
                "name": "Entitlement Manager Cash 1",
                "program_id": cls.program.id,
            }
        )

    @patch(
        "odoo.addons.spp_entitlement_cash.models.entitlement_manager.G2PCashEntitlementManager._get_addl_entitlement_fields"
    )
    def test_cash_get_addl_entitlement_fields(self, mock_super):
        self._common_test_get_addl_entitlement_fields(self.cash_entitlement_manager, mock_super)
