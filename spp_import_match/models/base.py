# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def load(self, fields, data):
        usable, field_to_match = self.env["spp.import.match"]._usable_rules(
            self._name,
            fields,
            option_config_ids=self.env.context.get("import_match_ids", []),
        )
        if usable:
            newdata = list()
            if ".id" in fields:
                column = fields.index(".id")
                fields[column] = "id"
                for values in data:
                    dbid = int(values[column])
                    values[column] = self.browse(dbid).get_external_id().get(dbid)
            import_fields = list(map(models.fix_import_export_id_paths, fields))
            converted_data = list(
                self._convert_records(self._extract_records(import_fields, data))
            )

            if "id" not in fields:
                fields.append("id")
                import_fields.append(["id"])
            clean_fields = []
            for f in import_fields:
                field_name = f[0]
                if len(f) > 1:
                    field_name += "/" + f[1]
                clean_fields.append(field_name)
            for dbid, xmlid, record, info in converted_data:
                row = dict(zip(clean_fields, data[info["record"]]))

                match = self
                if xmlid:
                    row["id"] = xmlid
                    newdata.append(tuple(row[f] for f in clean_fields))
                    continue
                elif dbid:
                    match = self.browse(dbid)
                else:
                    match = self.env["spp.import.match"]._match_find(self, record, row)

                if match:
                    flat_fields_to_remove = [
                        item for sublist in field_to_match for item in sublist
                    ]
                    for fields_pop in flat_fields_to_remove:
                        # TODO: @eMJay0921: import matching should not remove any
                        # value of importing row, this should be removed.
                        if fields_pop in row and match._fields[fields_pop].type in [
                            "one2many",
                            "many2many",
                        ]:
                            row[fields_pop] = False

                match.export_data(fields)

                ext_id = match.get_external_id()
                row["id"] = ext_id[match.id] if match else row.get("id", "")
                newdata.append(tuple(row[f] for f in fields))
            data = newdata
        return super().load(fields, data)

    def write(self, vals):
        model = self.env["ir.model"].sudo().search([("model", "=", self._name)])
        new_vals = vals.copy()
        for rec in vals:
            field_name = rec
            if not vals[field_name]:
                field = self.env["ir.model.fields"].search(
                    [("model_id", "=", model.id), ("name", "=", field_name)]
                )
                if field and field.ttype in ("one2many", "many2many"):
                    new_vals.pop(rec)
        return super().write(new_vals)
