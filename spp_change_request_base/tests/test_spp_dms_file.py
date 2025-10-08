import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestDMSFile(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.directory_id = cls.env["spp.dms.directory"].create(
            {
                "name": "Test Directory",
            }
        )

    def test_01_action_save_and_close(self):
        """Test action_save_and_close method."""
        dms_file = self.env["spp.dms.file"].create(
            {
                "name": "Test DMS File",
                "directory_id": self.directory_id.id,
            }
        )
        result = dms_file.action_save_and_close()
        self.assertEqual(result, {"type": "ir.actions.act_window_close"})

    def test_02_action_close(self):
        """Test action_close method."""
        dms_file = self.env["spp.dms.file"].create(
            {
                "name": "Test DMS File",
                "directory_id": self.directory_id.id,
            }
        )
        result = dms_file.action_close()
        self.assertEqual(result, {"type": "ir.actions.act_window_close"})

    def test_03_action_attach_documents(self):
        """Test action_attach_documents method."""
        dms_file = self.env["spp.dms.file"].create(
            {
                "name": "Test DMS File",
                "directory_id": self.directory_id.id,
            }
        )
        result = dms_file.action_attach_documents()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "spp.dms.file")
        self.assertEqual(result["res_id"], dms_file.id)
        self.assertIn("Upload Document", result["name"])
        self.assertIn("category_readonly", result["context"])
