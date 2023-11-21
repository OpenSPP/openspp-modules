# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def load(self, fields, data):
        usable, field_to_match = self.env["spp.import.match"]._usable_rules(
            self._name, fields
        )
        import_match = self.env["spp.import.match"].search(
            [("model_name", "=", self._name)]
        )
        overwrite_match = import_match[0].overwrite_match if import_match else False

        if usable:
            newdata = list()
            if ".id" in fields:
                column = fields.index(".id")
                fields[column] = "id"
                for values in data:
                    dbid = int(values[column])
                    values[column] = self.browse(dbid).get_external_id().get(dbid)
            import_fields = list(map(models.fix_import_export_id_paths, fields))
            converted_data = self._convert_records(
                self._extract_records(import_fields, data)
            )

            if "id" not in fields:
                fields.append("id")
                import_fields.append(["id"])

            clean_fields = [f[0] for f in import_fields]
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

                flat_fields_to_remove = [
                    item for sublist in field_to_match for item in sublist
                ]
                for fields_pop in flat_fields_to_remove:
                    if fields_pop in fields:
                        fields.remove(fields_pop)

                match.export_data(fields)

                ext_id = match.get_external_id()
                add_row = False
                if ext_id:
                    if overwrite_match:
                        add_row = True
                else:
                    add_row = True

                if add_row:
                    row["id"] = ext_id[match.id] if match else row.get("id", "")
                    newdata.append(tuple(row[f] for f in fields))
            data = newdata
        return super().load(fields, data)
