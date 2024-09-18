import base64
import unittest
from unittest.mock import patch
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from spp_dms.models.dms_file import SPPDMSFile

class TestSPPDMSFile(TransactionCase):

    def setUp(self):
        super(TestSPPDMSFile, self).setUp()
        self.dms_file = self.env['spp.dms.file'].create({
            'name': 'Test File',
            'directory_id': self.env['spp.dms.directory'].create({'name': 'Test Directory'}).id,
            'content': base64.b64encode(b'Test Content'),
        })

    def test_compute_path_with_display_name(self):
        self.dms_file.display_name = 'Test Display Name'
        self.dms_file._compute_path()
        self.assertEqual(self.dms_file.path_names, '/Test Directory/Test Display Name')
        self.assertIsNotNone(self.dms_file.path_json)

    def test_compute_path_without_display_name(self):
        self.dms_file.display_name = False
        self.dms_file._compute_path()
        self.assertEqual(self.dms_file.path_names, '/')
        self.assertIsNone(self.dms_file.path_json)

    def test_compute_content_with_content_file(self):
        self.dms_file.content_file = base64.b64encode(b'Test Content File')
        self.dms_file._compute_content()
        self.assertEqual(self.dms_file.content, base64.b64encode(b'Test Content File'))

    def test_compute_content_without_content_file(self):
        self.dms_file.content_file = False
        self.dms_file._compute_content()
        self.assertEqual(self.dms_file.content, base64.b64encode(b'Test Content'))

    def test_inverse_content(self):
        self.dms_file._inverse_content()
        self.assertEqual(self.dms_file.content_file, base64.b64encode(b'Test Content'))

    def test_compute_extension(self):
        self.dms_file._compute_extension()
        self.assertEqual(self.dms_file.extension, '.txt')

    def test_compute_mimetype(self):
        self.dms_file._compute_mimetype()
        self.assertEqual(self.dms_file.mimetype, 'text/plain')

    def test_compute_human_size(self):
        self.dms_file._compute_human_size()
        self.assertEqual(self.dms_file.human_size, '12 Bytes')

    def test_compute_image_1920_with_supported_mimetype(self):
        self.dms_file.mimetype = 'image/png'
        self.dms_file._compute_image_1920()
        self.assertEqual(self.dms_file.image_1920, base64.b64encode(b'Test Content'))

    def test_compute_image_1920_with_unsupported_mimetype(self):
        self.dms_file.mimetype = 'application/pdf'
        self.dms_file._compute_image_1920()
        self.assertIsNone(self.dms_file.image_1920)
