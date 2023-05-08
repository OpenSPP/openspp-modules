from base64 import b64encode
from os.path import dirname, join, realpath

from odoo.tests import TransactionCase

EXAMPLE_DIR = join(realpath(dirname(__file__)), "excel_files")


def from_excel_file(file_name):
    full_file_loc = join(EXAMPLE_DIR, file_name)
    with open(full_file_loc, "rb") as file:
        return b64encode(file.read())


class TestAreaImport(TransactionCase):
    def setUp(self):
        super().setUp()
        self._import = self.env["spp.area.import"].create(
            {
                "name": "Test Import",
            }
        )
        self._model = self.env["spp.area"]

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
        self.assertEqual(self._import.tot_rows_error, 1, "Total rows error should be 1")

    def test_04_import_data(self):
        self._import.excel_file = from_excel_file("level_area_2.xlsx")
        with self.assertLogs("odoo.addons.spp_area.models.area_import") as log_catcher:
            self._import.import_data()
            for o in log_catcher.output:
                self.assertRegex(
                    o,
                    "^INFO:odoo.addons.spp_area.models.area_import:.*$",
                    "Should be info log level!",
                )
        self.assertEqual(
            self._import.tot_rows_imported, 6, "Total rows imported should be 6"
        )
        self.assertEqual(self._import.tot_rows_error, 0, "Total rows error should be 0")
        self.assertEqual(self._import.state, "Imported", "state should be Imported")

    def test_05_save_to_area(self):
        self._import.excel_file = from_excel_file("level_area_2.xlsx")
        to_create_area = self._model.search(
            [("code", "in", ["IQ", "28.0", "641", "642"])]
        )
        self.assertFalse(to_create_area.ids, "Area not yet existed!")
        self._import.import_data()
        self._import.save_to_area()
        to_create_area = self._model.search(
            [("code", "in", ["IQ", "28.0", "641", "642"])]
        )
        self.assertTrue(to_create_area.ids, "Areas should be created!")
        self.assertEqual(self._import.state, "Done", "state should be Done")
