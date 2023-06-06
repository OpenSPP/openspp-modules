# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OpenSPPHouseVisitMixin(models.AbstractModel):
    _name = "spp.event.house.visit.mixin"
    _description = "House Visit Mixin"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    summary = fields.Char()
    is_farm = fields.Boolean(default=False)
    farm_size_acre = fields.Float()
    photo = fields.Binary()
    photo_filename = fields.Char()
    number_of_pigs = fields.Integer()
    number_of_cows = fields.Integer()
    no_food_stock = fields.Integer()
    disabled = fields.Boolean(default=False)


class OpenSPPHouseVisit(models.Model):
    _name = "spp.event.house.visit"
    _description = "House Visit"
    _inherit = ["spp.event.house.visit.mixin"]

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return (
            self.env["ir.ui.view"]
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )


class OpenSPPHouseVisitRaw(models.Model):
    _name = "spp.event.house.visit.raw"
    _description = "House Visit Raw Data"
    _inherit = ["spp.event.house.visit.mixin"]

    registrant_given_name = fields.Char()
    registrant_family_name = fields.Char()
    registrant_id = fields.Many2one("res.partner")
    state = fields.Selection(
        [
            ("New", "New"),
            ("Validated", "Validated"),
            ("Error", "Error"),
            ("Updated", "Updated"),
            ("Posted", "Posted"),
        ],
        "Status",
        readonly=True,
        default="New",
    )
    remarks = fields.Char()
    import_id = fields.Many2one("spp.event.data.import")


class OpenSPPEventDataImport(models.Model):
    _inherit = "spp.event.data.import"

    spp_event_house_visit = fields.One2many("spp.event.house.visit.raw", "import_id")

    def spp_event_house_visit_import(self, sheet):  # noqa: C901
        for rec in self:
            vals = []
            columns = []
            mainvals = {}
            for row in range(1, sheet.nrows):

                registrant_given_name = None
                registrant_family_name = None
                summary = None
                is_farm = None
                farm_size_acre = None
                number_of_pigs = None
                number_of_cows = None
                no_food_stock = None
                disabled = None
                state = "Validated"
                errctr = 0
                remarks = ""
                for col in range(sheet.ncols):
                    col_value = sheet.cell(row, col).value
                    if col_value == "<Null>":
                        col_value = ""
                    col_name = sheet.cell(0, col).value
                    if col_name.find("registrant_given_name") >= 0:
                        registrant_given_name = col_value
                        if not col_value:
                            errctr += 1
                            state = "Error"
                            remarks += str(errctr) + ".) Given Name cannot be blank; "
                    elif col_name.find("registrant_family_name") >= 0:
                        registrant_family_name = col_value
                        if not col_value:
                            errctr += 1
                            state = "Error"
                            remarks += str(errctr) + ".) Family Name cannot be blank; "
                    elif col_name.find("summary") >= 0:
                        summary = col_value
                    elif col_name.find("is_farm") >= 0:
                        is_farm = col_value
                    elif col_name.find("farm_size_acre") >= 0:
                        farm_size_acre = col_value
                    elif col_name.find("number_of_pigs") >= 0:
                        number_of_pigs = col_value
                    elif col_name.find("number_of_cows") >= 0:
                        number_of_cows = col_value
                    elif col_name.find("no_food_stock") >= 0:
                        no_food_stock = col_value
                    elif col_name.find("disabled") >= 0:
                        disabled = col_value

                # Store values to columns
                columns.append(
                    {
                        "registrant_given_name": registrant_given_name,
                        "registrant_family_name": registrant_family_name,
                        "summary": summary,
                        "is_farm": is_farm,
                        "farm_size_acre": farm_size_acre,
                        "number_of_pigs": number_of_pigs,
                        "number_of_cows": number_of_cows,
                        "no_food_stock": no_food_stock,
                        "disabled": disabled,
                        "state": state,
                        "remarks": remarks,
                    }
                )

            for val in columns:
                vals.append([0, 0, val])

            _logger.info(
                "Event Data Import: Updating Record: %s" % fields.Datetime.now()
            )
            mainvals.update(
                {
                    "date_imported": fields.Datetime.now(),
                    "import_id": self.env.user,
                    "date_validated": fields.Datetime.now(),
                    "validate_id": self.env.user,
                    "state": "Imported",
                    "spp_event_house_visit": vals,
                }
            )
            rec.update(mainvals)

            _logger.info("Event Data Import: Completed: %s" % fields.Datetime.now())

    def spp_event_house_visit_save(self):
        for rec in self:
            error_ctr = 0
            for raw in rec.spp_event_house_visit:
                if raw.state == "Validated":
                    if raw.registrant_given_name and raw.registrant_family_name:
                        registrant = self.env["res.partner"].search(
                            [
                                ("given_name", "=", raw.registrant_given_name),
                                ("family_name", "=", raw.registrant_family_name),
                            ]
                        )
                        if registrant:
                            event_vals = {
                                "summary": raw.summary,
                                "is_farm": raw.is_farm,
                                "farm_size_acre": raw.farm_size_acre,
                                "number_of_pigs": raw.number_of_pigs,
                                "number_of_cows": raw.number_of_cows,
                                "no_food_stock": raw.no_food_stock,
                                "disabled": raw.disabled,
                            }
                            event = self.env[rec.event_data_model].create(event_vals)
                            event_data_vals = {
                                "model": rec.event_data_model,
                                "partner_id": registrant.id,
                                "collection_date": fields.date.today() or False,
                                "expiry_date": False,
                                "res_id": event.id,
                            }
                            self.env["spp.event.data"].create(event_data_vals)
                            registrant._compute_active_house_visit()
                            raw.update({"state": "Posted"})
                        else:
                            error_ctr += 1
                            raw.update(
                                {"state": "Error", "remarks": "Registrant Not Found!"}
                            )
                    else:
                        error_ctr += 1
                        raw.update({"state": "Error", "remarks": "No Registrant!"})
                else:
                    error_ctr += 1
                    raw.update({"state": "Error", "remarks": "Not Validated!"})

            if error_ctr == 0:
                rec.update({"state": "Done"})

    @api.model
    def _selection_event_data_model_id(self):
        selection = super()._selection_event_data_model_id()
        new_event_type = (
            "spp.event.house.visit",
            "House Visit",
        )
        if new_event_type not in selection:
            selection.append(new_event_type)
        return selection
