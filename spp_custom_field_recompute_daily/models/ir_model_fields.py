import logging

from pytz import timezone

from odoo import SUPERUSER_ID, api, fields, models

_logger = logging.getLogger(__name__)


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    recompute_daily = fields.Boolean(
        string="Daily Recompute",
        default=False,
        help="Whether or not this field should be recompute daily by cron jobs!",
    )

    def _reflect_field_params(self, field, model_id):
        vals = super()._reflect_field_params(field, model_id)
        compute = getattr(field, "compute", False) or getattr(field, "related", False)
        store = getattr(field, "store", False)
        recompute_daily = getattr(field, "recompute_daily", False)
        if recompute_daily and not all([compute, store]):
            _logger.warning(
                f"Non-compute-stored field: ({field.name}, {field.string}) on model '{field.model_name}' "
                "is not allowed to be recomputed daily!"
            )
            recompute_daily = False
        vals["recompute_daily"] = recompute_daily
        return vals

    def _instanciate_attrs(self, field_data):
        attrs = super()._instanciate_attrs(field_data)
        if attrs and field_data.get("recompute_daily"):
            attrs["recompute_daily"] = field_data["recompute_daily"]
        return attrs

    @api.model
    def _daily_recompute_indicators(self):
        maximum_daily_recompute_count = int(
            self.env["ir.config_parameter"].sudo().get_param("spp.maximum_daily_recompute_count", "10_000")
        )
        recompute_daily_fields = self.search([("recompute_daily", "=", True)])
        for field in recompute_daily_fields:
            model = self.env[field.model_id.model]
            total_records_count = model.search_count([])
            records = model.search([])
            if total_records_count <= maximum_daily_recompute_count:
                field._recompute_indicator_on_records(records)
                continue
            for i in range(0, total_records_count, maximum_daily_recompute_count):
                field.with_delay()._recompute_indicator_on_records(records[i : (i + maximum_daily_recompute_count)])

    def _recompute_indicator_on_records(self, records_to_compute):
        self.ensure_one()
        return self.env.add_to_compute(records_to_compute._fields[self.name], records_to_compute)

    @api.model
    def create_daily_recompute_cron(self):
        ADMINUSER_ID = 2
        self = self.with_user(ADMINUSER_ID)
        tz = self._context.get("tz") or self.env.user.tz or "UTC"
        local = timezone(tz)
        local_1am = local.localize(
            fields.Datetime.add(fields.Datetime.now(), days=1).replace(hour=1, minute=0, second=0)
        )
        utc_for_local_1am = local_1am.astimezone(timezone("utc"))
        self.env["ir.cron"].sudo().create(
            {
                "name": "## Indicator: Daily Recompute Fields",
                "interval_number": 1,
                "interval_type": "days",
                "numbercall": -1,
                "doall": False,
                "model_id": self.env.ref("base.model_ir_model_fields").id,
                "state": "code",
                "code": "model._daily_recompute_indicators()",
                "nextcall": utc_for_local_1am.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": SUPERUSER_ID,
            }
        )
