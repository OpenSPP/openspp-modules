from odoo.tests import TransactionCase


class TestResConfigSettings(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._config = cls.env["ir.config_parameter"]
        cls._settings = cls.env["res.config.settings"].create({})

    def test_01_get_auto_approve_id_request(self):
        self._config.set_param("spp_id_queue.auto_approve_id_request", False)
        self.assertFalse(
            self._settings.auto_approve_id_request,
            "Value of `auto_approve_id_request` should be False!",
        )

    def test_02_set_auto_approve_id_request(self):
        self._settings.write({"auto_approve_id_request": False})
        self.assertFalse(
            self._config.get_param("spp_id_queue.auto_approve_id_request"),
            "Config Parameter `auto_approve_id_request` should be False as well!",
        )
