from odoo.tests import TransactionCase


class TestAreaImport(TransactionCase):
    def setUp(self):
        super().setUp()
        self._import = self.env["spp.area.import"].create(
            {
                "name": "Test Import",
            }
        )

    def test_01_cancel_import(self):
        self.assertEqual(self._import.state, "New", "Import should in New state")
        self._import.cancel_import()
        self.assertEqual(
            self._import.state, "Cancelled", "Import should in Cancelled state"
        )

    def test_02_excel_file_change(self):
        self._import.excel_file_change()
        self.assertEqual(
            self._import.upload_id, self.env.user, "User should be the one who upload!"
        )
        self.assertEqual(
            self._import.state, "Uploaded", "Import should in Uploaded state"
        )
        self._import.name = ""
        self._import.excel_file_change()
        self.assertFalse(
            self._import.upload_id, "User should not be the one who upload!"
        )
        self.assertEqual(self._import.state, "New", "Import should in New state")

    def test_03_compute_get_total_rows(self):
        self._import.write(
            {
                "raw_data_ids": [
                    (0, 0, {"state": "New"}),
                    (0, 0, {"state": "New"}),
                    (0, 0, {"state": "Error"}),
                ]
            }
        )
        self.assertEqual(
            self._import.tot_rows_imported, 3, "Total rows imported should be 3"
        )
        self.assertEqual(
            self._import.tot_rows_error, 1, "Total rows imported should be 1"
        )
