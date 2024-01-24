import base64
import os

from odoo.tests.common import TransactionCase


class AreaImportTestMixin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(AreaImportTestMixin, cls).setUpClass()
        # Greater than or equal to 400 rows
        xls_file = None
        xls_file_name = None

        file_path = f"{os.path.dirname(os.path.abspath(__file__))}/irq_adminboundaries_tabulardata.xlsx"
        with open(file_path, "rb") as f:
            xls_file_name = f.name
            xls_file = base64.b64encode(f.read())

        cls.area_import_id = cls.env["spp.area.import"].create(
            {
                "excel_file": xls_file,
                "name": xls_file_name,
                "state": "Uploaded",
            }
        )

        # Less than 400 rows
        xls_file_2 = None
        xls_file_name_2 = None

        file_path_2 = f"{os.path.dirname(os.path.abspath(__file__))}/pse_adminboundaries_tabulardata.xlsx"
        with open(file_path_2, "rb") as f:
            xls_file_name_2 = f.name
            xls_file_2 = base64.b64encode(f.read())

        cls.area_import_id_2 = cls.env["spp.area.import"].create(
            {
                "excel_file": xls_file_2,
                "name": xls_file_name_2,
                "state": "Uploaded",
            }
        )
