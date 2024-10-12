from odoo import api, models


class Company(models.Model):
    _inherit = "res.company"

    @api.model
    def update_ph_data(self):
        main_company = self.env.ref("base.main_company")
        main_company.update(
            {
                "currency_id": self.env.ref("base.PHP").id,
                "country_id": self.env.ref("base.ph").id,
            }
        )
