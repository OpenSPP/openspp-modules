import logging

from .common import AreaImportTestMixin

_logger = logging.getLogger(__name__)


class AreaImportTest(AreaImportTestMixin):
    def test_01_cancel_import(self):
        self.area_import_id.cancel_import()

        self.assertEqual(self.area_import_id.state, "Cancelled")

    def test_02_reset_to_uploaded(self):
        self.area_import_id.reset_to_uploaded()

        self.assertEqual(self.area_import_id.state, "Uploaded")

    def test_03_import_data(self):
        self.area_import_id.import_data()

        raw_data_ids = self.area_import_id.raw_data_ids

        self.assertEqual(len(raw_data_ids.ids), self.area_import_id.tot_rows_imported)
        self.assertEqual(0, self.area_import_id.tot_rows_error)
        self.assertEqual(self.area_import_id.state, "Imported")
        self.assertEqual(
            self.env["spp.area.import.raw"].search(
                [("id", "in", raw_data_ids.ids), ("state", "=", "New")], count=True
            ),
            self.area_import_id.tot_rows_imported,
        )

    def test_04_validate_raw_data(self):
        self.area_import_id.import_data()
        has_error = self.area_import_id.validate_raw_data()

        raw_data_ids = self.area_import_id.raw_data_ids

        self.assertFalse(has_error)
        self.assertEqual(len(raw_data_ids.ids), self.area_import_id.tot_rows_imported)
        self.assertEqual(0, self.area_import_id.tot_rows_error)
        self.assertEqual(self.area_import_id.state, "Validated")
        self.assertEqual(
            self.env["spp.area.import.raw"].search(
                [("id", "in", raw_data_ids.ids), ("state", "=", "Validated")],
                count=True,
            ),
            self.area_import_id.tot_rows_imported,
        )

    def test_05_save_to_area(self):
        self.area_import_id.import_data()
        self.area_import_id.validate_raw_data()
        self.area_import_id.save_to_area()

        raw_data_ids = self.area_import_id.raw_data_ids

        self.assertEqual(len(raw_data_ids.ids), self.area_import_id.tot_rows_imported)
        self.assertEqual(0, self.area_import_id.tot_rows_error)
        self.assertEqual(self.area_import_id.state, "Done")

        for raw_data_id in raw_data_ids:
            self.assertTrue(
                bool(
                    self.env["spp.area"].search(
                        [
                            ("draft_name", "=", raw_data_id.admin_name),
                            ("code", "=", raw_data_id.admin_code),
                        ],
                        limit=1,
                    )
                )
            )
