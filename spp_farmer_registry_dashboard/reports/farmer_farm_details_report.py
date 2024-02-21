from odoo import api, fields, models


class FarmDetailsReport(models.Model):
    _name = "farm.details.report"
    _description = "Farm Details Statistics"
    _auto = False

    name = fields.Char(string="Farm Name", readonly=True)
    registration_date = fields.Date(readonly=True)
    graph_footer = fields.Char(readonly=True)
    land_water_management_crop_rotation = fields.Char(string="Crop Rotation", readonly=True)
    land_water_management_green_cover_crop = fields.Char(string="Green cover crop", readonly=True)
    land_water_management_contour_ploughing = fields.Char(string="Contour ploughing/Ridging", readonly=True)

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
                'Sustainable Land and Environmental Management' AS graph_footer,
                CASE
                    WHEN dtl.land_water_management_crop_rotation THEN
                        'Crop Rotation'
                    ELSE
                        NULL
                END AS land_water_management_crop_rotation,
                CASE
                    WHEN dtl.land_water_management_green_cover_crop THEN
                        'Green cover crop'
                    ELSE
                        NULL
                END AS land_water_management_green_cover_crop,
                CASE
                    WHEN dtl.land_water_management_contour_ploughing THEN
                        'Contour ploughing/Ridging'
                    ELSE
                        NULL
                END AS land_water_management_contour_ploughing
        """

    @api.model
    def _from(self):
        return """
            FROM res_partner AS farm
                LEFT JOIN spp_farm_details AS dtl ON dtl.id = farm.farm_detail_id
        """

    @api.model
    def _where(self):
        return """
            WHERE farm.active = True
                AND farm.is_group = True
        """
