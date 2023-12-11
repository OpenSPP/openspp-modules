from odoo.tests import TransactionCase


class TestIrUiMenu(TransactionCase):
    def test_01_visible_menu_ids(self):
        def set_show_spp_starter(vals: bool) -> bool:
            key = "spp_starter.show_spp_starter"
            return self.env["ir.config_parameter"].sudo().set_param(key, str(vals))

        menu_obj = self.env["ir.ui.menu"].with_context(**{"ir.ui.menu.full_list": True})
        set_show_spp_starter(True)
        self.assertNotIn(
            self.env.ref("base.menu_management").id,
            menu_obj._visible_menu_ids(),
            "Real Apps Menu should not be shown!",
        )
        self.assertIn(
            self.env.ref("spp_starter.spp_starter_menu").id,
            menu_obj._visible_menu_ids(),
            "Fake Apps Menu should be shown!",
        )
        set_show_spp_starter(False)
        self.assertIn(
            self.env.ref("base.menu_management").id,
            menu_obj._visible_menu_ids(),
            "Real Apps Menu should be shown!",
        )
        self.assertNotIn(
            self.env.ref("spp_starter.spp_starter_menu").id,
            menu_obj._visible_menu_ids(),
            "Fake Apps Menu should not be shown!",
        )
