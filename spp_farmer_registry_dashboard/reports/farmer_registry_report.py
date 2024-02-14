from odoo import api, fields, models


class FarmerRegistryReport(models.Model):
    _name = "farmer.registry.report"
    _description = "Farmer Registry Statistics"
    _auto = False
    _order = "registration_date desc"

    name = fields.Char(string="Farm Name", readonly=True)
    registration_date = fields.Date(readonly=True)
    financial_services_main_income_source = fields.Selection(
        [
            ("sale of farming produce", "Sale of farming produce"),
            ("non-farm trading", "Non-farm trading"),
            ("salary from employment elsewhere", "Salary from employment elsewhere"),
            ("casual labor elsewhere", "Casual labor elsewhere"),
            ("pension", "Pension"),
            ("remittances", "Remittances"),
            ("cash transfer", "Cash transfer"),
            ("other", "Other"),
        ],
        string="What is your main source of income by priority?",
        readonly=True,
    )
    financial_services_percentage_of_income_from_farming = fields.Float(
        string="What percentage of your income comes from farming activities?",
        readonly=True,
    )
    land_acreage = fields.Float(
        readonly=True,
    )
    details_legal_status = fields.Selection(
        [
            ("self", "Owned by self"),
            ("family", "Owned by family"),
            ("extended community", "Owned by extended community"),
            ("cooperative", "Owned by cooperative"),
            ("government", "Owned by Government"),
            ("leased", "Leased from actual owner"),
            ("unknown", "Do not Know"),
        ],
        string="Legal Status",
        readonly=True,
    )

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
                dtl.financial_services_main_income_source AS financial_services_main_income_source,
                dtl.financial_services_percentage_of_income_from_farming
                    AS financial_services_percentage_of_income_from_farming,
                lr.land_acreage AS land_acreage,
                dtl.details_legal_status AS details_legal_status
        """

    @api.model
    def _from(self):
        return """
            FROM res_partner AS farm
                LEFT JOIN spp_land_record AS lr ON lr.id = farm.farm_land_rec_id
                LEFT JOIN spp_farm_details AS dtl ON dtl.id = farm.farm_detail_id
        """

    @api.model
    def _where(self):
        return """
            WHERE farm.active = True
                AND farm.is_group = True
        """
