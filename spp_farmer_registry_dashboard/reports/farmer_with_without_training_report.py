from odoo import api, fields, models


class FarmerWithWithoutTrainingReport(models.Model):
    _name = "farmer.with.without.training.report"
    _description = "Farmer With/Without Formal Training Statistics"
    _auto = False

    name = fields.Char(string="Farm Name", readonly=True)
    registration_date = fields.Date(readonly=True)
    formal_agricultural_training_yn = fields.Char("With formal training in agriculture", readonly=True)
    formal_agricultural_training = fields.Boolean("Do you have formal training in agriculture?", readonly=True)

    @property
    def _table_query(self):
        return f"{self._select()} {self._from()} {self._where()}"

    @api.model
    def _select(self):
        return """
            SELECT
                farm.id,
                farm.name AS name,
                farm.registration_date AS registration_date,
                farm.formal_agricultural_training AS formal_agricultural_training,
                CASE
                    WHEN farm.formal_agricultural_training THEN
                        'Yes'
                    ELSE
                        'No'
                END AS formal_agricultural_training_yn
        """

    @api.model
    def _from(self):
        return """
            FROM res_partner AS farm
        """

    @api.model
    def _where(self):
        return """
            WHERE farm.active = True
                AND farm.is_group = True
        """
