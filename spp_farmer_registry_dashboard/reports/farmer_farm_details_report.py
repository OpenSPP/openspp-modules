from odoo import api, fields, models


class FarmDetailsReport(models.Model):
    _name = "farm.details.report"
    _description = "Farm Details Statistics"
    _auto = False

    name = fields.Char(string="Farm Name", readonly=True)
    registration_date = fields.Date(readonly=True)
    land_water_management_crop_rotation = fields.Integer(
        string="Crop Rotation", readonly=True
    )
    land_water_management_green_cover_crop = fields.Integer(
        string="Green cover crop", readonly=True
    )
    land_water_management_contour_ploughing = fields.Integer(
        string="Contour ploughing/Ridging", readonly=True
    )

    @property
    def _table_query(self):
        return "%s %s %s" % (self._select(), self._from(), self._where())

    @api.model
    def _select(self):
        return """
            SELECT
                farm.id,
                farm.name AS name,
                farm.registration_date AS registration_date,
                CASE
                    WHEN dtl.land_water_management_crop_rotation THEN
                        1
                    ELSE
                        0
                END AS land_water_management_crop_rotation,
                CASE
                    WHEN dtl.land_water_management_green_cover_crop THEN
                        1
                    ELSE
                        0
                END AS land_water_management_green_cover_crop,
                CASE
                    WHEN dtl.land_water_management_contour_ploughing THEN
                        1
                    ELSE
                        0
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
