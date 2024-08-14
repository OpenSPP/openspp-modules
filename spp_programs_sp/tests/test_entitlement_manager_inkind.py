from unittest.mock import patch

from .common import Common


class DefaultEntitlementManagerTest(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inkind_entitlement_manager = cls.env["g2p.program.entitlement.manager.inkind"].create(
            {
                "name": "Entitlement Manager In-Kind 1",
                "program_id": cls.program.id,
            }
        )

    @patch(
        "odoo.addons.spp_entitlement_in_kind.models.entitlement_manager.G2PInKindEntitlementManager._get_addl_entitlement_fields"
    )
    def test_cash_get_addl_entitlement_fields(self, mock_super):
        self._common_test_get_addl_entitlement_fields(self.inkind_entitlement_manager, mock_super)
