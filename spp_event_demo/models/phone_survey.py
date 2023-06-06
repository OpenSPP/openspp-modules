# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OpenSPPPhoneSurveyMixin(models.AbstractModel):
    _name = "spp.event.phone.survey.mixin"
    _description = "Phone Survey Mixin"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    summary = fields.Char()
    description = fields.Text()


class OpenSPPPhoneSurvey(models.Model):
    _name = "spp.event.phone.survey"
    _description = "Phone Survey"
    _inherit = ["spp.event.phone.survey.mixin"]

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return (
            self.env["ir.ui.view"]
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )


class OpenSPPPhoneSurveyRaw(models.Model):
    _name = "spp.event.phone.survey.raw"
    _description = "Phone Survey Raw Data"
    _inherit = ["spp.event.phone.survey.mixin"]

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

    spp_event_phone_survey = fields.One2many("spp.event.phone.survey.raw", "import_id")

    def spp_event_phone_survey_import(self, sheet):
        for rec in self:
            vals = []
            columns = []
            mainvals = {}
            for row in range(sheet.nrows):
                if row > 0:  # Ignore First Row containing column headings
                    registrant_given_name = None
                    registrant_family_name = None
                    summary = None
                    description = None
                    state = "Validated"
                    errctr = 0
                    remarks = ""
                    for col in range(1, sheet.ncols):
                        col_value = sheet.cell(row, col).value
                        if col_value == "<Null>":
                            col_value = ""
                        col_name = sheet.cell(0, col).value
                        if col_name.find("registrant_given_name") >= 0:
                            registrant_given_name = col_value
                            if not col_value:
                                errctr += 1
                                state = "Error"
                                remarks += (
                                    str(errctr) + ".) Given Name cannot be blank; "
                                )
                        elif col_name.find("registrant_family_name") >= 0:
                            registrant_family_name = col_value
                            if not col_value:
                                errctr += 1
                                state = "Error"
                                remarks += (
                                    str(errctr) + ".) Family Name cannot be blank; "
                                )
                        elif col_name.find("summary") >= 0:
                            summary = col_value
                        elif col_name.find("description") >= 0:
                            description = col_value

                    # Store values to columns
                    columns.append(
                        {
                            "registrant_given_name": registrant_given_name,
                            "registrant_family_name": registrant_family_name,
                            "summary": summary,
                            "description": description,
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
                    "spp_event_phone_survey": vals,
                }
            )
            rec.update(mainvals)

            _logger.info("Event Data Import: Completed: %s" % fields.Datetime.now())

    def spp_event_phone_survey_save(self):
        for rec in self:
            error_ctr = 0
            for raw in rec.spp_event_phone_survey:
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
                                "description": raw.description,
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
            "spp.event.phone.survey",
            "Phone Survey",
        )
        if new_event_type not in selection:
            selection.append(new_event_type)
        return selection
