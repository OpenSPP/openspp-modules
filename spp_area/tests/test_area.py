# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.
import base64
import logging
from os import path

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)

PATH = path.join(path.dirname(__file__), "import_data", "%s.xlsx")
OPTIONS = {
    "headers": True,
    "quoting": '"',
    "separator": ",",
}


class AreaTest(TransactionCase):
    def setUp(self):
        super().setUp()

        # Initial Setup of Variables
        self.area_1 = self.env["spp.area"].create(
            {
                "draft_name": "Testing Area",
            }
        )
        self.area_1_child = self.env["spp.area"].create(
            {
                "draft_name": "Testing Area Child",
                "parent_id": self.area_1.id,
            }
        )

    def create_import_area(self, filename):
        fo = open(PATH % filename, "rb").read()
        base64_encoded = base64.b64encode(fo).decode("UTF-8")
        return self.env["spp.area.import"].create(
            {
                "excel_file": base64_encoded,
                "name": "%s.xlsx" % filename,
            }
        )

    def test_01_check_childs(self):
        self.area_1._compute_get_childs()

        self.assertEqual(len(self.area_1.child_ids), 1)

    def test_02_import_data(self):
        import_data = self.create_import_event_data("test")
        import_data.import_data()
        import_data.save_to_area()

        areas = self.env["spp.area"].browse()
        self.assertEqual(len(areas), 21)
