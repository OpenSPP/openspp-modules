import base64
import binascii
import hashlib
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestSPPDMSFile(TransactionCase):
    def setUp(self):
        super().setUp()
        self.dms_file = self.env["spp.dms.file"].create(
            {
                "name": "Test File",
                "directory_id": self.env["spp.dms.directory"].create({"name": "Test Directory"}).id,
                "content": base64.b64encode(b"Test Content"),
            }
        )

    def tearDown(self):
        self.dms_file.unlink()
        super().tearDown()

    @patch("spp_dms.models.dms_file.SPPDMSFile._get_checksum")
    def test_inverse_content(self, mock_checksum):
        mock_checksum.return_value = "fake_checksum"
        self.dms_file._inverse_content()
        self.assertEqual(self.dms_file.checksum, "fake_checksum")

    @patch("spp_dms.models.dms_file.file_tools.guess_extension")
    def test_compute_extension(self, mock_guess_extension):
        mock_guess_extension.return_value = ".fake"
        self.dms_file._compute_extension()
        self.assertEqual(self.dms_file.extension, ".fake")

    def test_compute_path_with_display_name(self):
        self.dms_file.display_name = "Test Display Name"
        self.dms_file._compute_path()
        self.assertEqual(self.dms_file.path_names, "/Test Directory/Test Display Name")
        self.assertIsNotNone(self.dms_file.path_json)

    def test_compute_path_without_display_name(self):
        self.dms_file.display_name = False
        self.dms_file._compute_path()
        self.assertEqual(self.dms_file.path_names, "/")
        self.assertIsNone(self.dms_file.path_json)

    def test_compute_content_with_content_file(self):
        self.dms_file.content_file = base64.b64encode(b"Test Content File")
        self.dms_file._compute_content()
        self.assertEqual(self.dms_file.content, base64.b64encode(b"Test Content File"))

    def test_compute_content_without_content_file(self):
        self.dms_file.content_file = False
        self.dms_file._compute_content()
        self.assertEqual(self.dms_file.content, base64.b64encode(b"Test Content"))

    def test_compute_content_with_large_file(self):
        large_content = base64.b64encode(b"a" * 10**6)
        self.dms_file.content_file = large_content
        self.dms_file._compute_content()
        self.assertEqual(self.dms_file.content, large_content)

    def test_compute_content_with_invalid_base64(self):
        self.dms_file.content_file = b"invalid base64 string"
        with self.assertRaises(binascii.Error):
            self.dms_file._compute_content()

    def test_checksum_calculation(self):
        binary_data = b"Test Content for Checksum"
        expected_checksum = hashlib.sha1(binary_data).hexdigest()
        checksum = self.dms_file._get_checksum(binary_data)
        self.assertEqual(checksum, expected_checksum)

    def test_compute_mimetype_with_invalid_content(self):
        self.dms_file.content = base64.b64encode(b"invalid content")
        self.dms_file._compute_mimetype()
        self.assertIsNone(self.dms_file.mimetype)

    def test_content_update_integrity(self):
        new_content = base64.b64encode(b"New Test Content")
        self.dms_file.content_file = new_content
        self.dms_file._compute_content()
        self.dms_file._inverse_content()
        self.dms_file._compute_extension()

        self.assertEqual(self.dms_file.content, new_content)
        self.assertEqual(self.dms_file.size, len(base64.b64decode(new_content)))
        self.assertEqual(self.dms_file.checksum, hashlib.sha1(base64.b64decode(new_content)).hexdigest())

    def test_compute_image_1920_with_unknown_mimetype(self):
        self.dms_file.mimetype = "application/unknown"
        self.dms_file._compute_image_1920()
        self.assertIsNone(self.dms_file.image_1920)
