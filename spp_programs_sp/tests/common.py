from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        country = cls.env.ref("base.iq")
        cls.service_point_1 = cls.env["spp.service.point"].create(
            {
                "name": "Agent1",
                "country_id": country.id,
                "phone_no": "+9647001234567",
                "is_disabled": False,
            }
        )
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "name": "Registrant 1 [TEST]",
                "is_registrant": True,
                "is_group": True,
                "service_point_ids": [(6, 0, cls.service_point_1.ids)],
            }
        )

        cls.program = cls.env["g2p.program"].create(
            {
                "name": "Program 1",
                "store_sp_in_entitlements": True,
            }
        )
        cls.program.create_journal()

    def _common_test_get_addl_entitlement_fields(self, entitlement_manager, mock_super):
        mock_return_value = {"test": "test"}
        mock_super.return_value = mock_return_value
        result = entitlement_manager._get_addl_entitlement_fields(self.registrant_1)
        self.assertEqual(result, {"test": "test", "service_point_ids": self.service_point_1})

        mock_super.return_value = None
        self.program.store_sp_in_entitlements = False
        result = entitlement_manager._get_addl_entitlement_fields(self.registrant_1)
        self.assertEqual(result, {"service_point_ids": None})
