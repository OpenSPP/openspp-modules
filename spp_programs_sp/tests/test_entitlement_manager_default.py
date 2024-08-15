from unittest.mock import patch

from .common import Common


class DefaultEntitlementManagerTest(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_entitlement_manager = cls.env["g2p.program.entitlement.manager.default"].create(
            {
                "name": "Entitlement Manager Default 1",
                "program_id": cls.program.id,
            }
        )

    @patch(
        "odoo.addons.spp_programs.models.managers.entitlement_manager_default.G2PDefaultEntitlementManagerCustom._get_addl_entitlement_fields"
    )
    def test_cash_get_addl_entitlement_fields(self, mock_super):
        self._common_test_get_addl_entitlement_fields(self.default_entitlement_manager, mock_super)
