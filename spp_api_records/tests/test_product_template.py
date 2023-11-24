import base64
import io

from PIL import Image

from odoo.tests import TransactionCase


class TestProductTemplate(TransactionCase):
    def setUp(self):
        super().setUp()
        # create a cached image
        f = io.BytesIO()
        Image.new("RGB", (800, 500), "#000000").save(f, "PNG")
        f.seek(0)
        image_black = base64.b64encode(f.read())
        self._product = self.env["product.template"].create(
            {
                "image_1920": image_black,
                "name": "TEST PRODUCT",
            }
        )

    def test_01_test(self):
        self.assertIn(
            f"/web/image?model=product.template&id={self._product.id}&field=image_512",
            self._product.image_url,
        )
