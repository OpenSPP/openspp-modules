from odoo.tests import TransactionCase


class TestIRModuleModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrModule = cls.env["ir.module.module"]

        cls.survey_module = cls.IrModule.search([("name", "=", "mail")], limit=1)
        cls.survey_module.button_install()

    def test_01_update_menu_icons(self):
        # Verify that the icon was updated
        self.survey_module.next()
        menu = self.env.ref("mail.menu_root_discuss")
        self.assertEqual(menu.web_icon, "spp_base_common,static/description/icon-Discuss-White-line.png")
