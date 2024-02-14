from odoo import api, fields, models


class ProductTemplateCustomization(models.Model):
    _inherit = "product.template"

    image_url = fields.Char(string="Product URL", compute="_compute_product_image_url")

    @api.depends("image_1920", "image_512")
    def _compute_product_image_url(self):
        """
        Generate the URL of product images (image_512).
        """
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            url = None
            if rec.image_1920:
                url = base_url + "/web/image?" + "model=product.template&id=" + str(rec.id) + "&field=image_512"

            rec.image_url = url
