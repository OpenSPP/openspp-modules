from __future__ import annotations

from collections.abc import Iterable, Sequence

from odoo import models


class OpensppIndicatorResolver(models.AbstractModel):
    _name = "openspp.indicator.resolver"
    _description = "OpenSPP Metrics Resolver"

    def map_subjects_to_external(
        self, subject_model: str, subject_ids: Sequence[int], fields_chain: Sequence[str], *, required: bool = False
    ) -> tuple[dict[int, str], list[int]]:
        """Return mapping internal subject -> external identifier for provider calls."""
        subject_ids = [int(sid) for sid in subject_ids if sid]
        if not subject_ids:
            return {}, []
        if not fields_chain:
            return {sid: sid for sid in subject_ids}, []
        Model = self.env[subject_model].sudo()
        recs = Model.browse(subject_ids)
        mapped: dict[int, str] = {}
        unmapped: list[int] = []
        for rec in recs:
            value = None
            for field in fields_chain:
                try:
                    value = getattr(rec, field)
                except Exception:
                    value = None
                if value:
                    break
            if value:
                mapped[rec.id] = value
            elif required:
                unmapped.append(rec.id)
            else:
                mapped[rec.id] = f"odoo:{rec.id}"
        return mapped, unmapped

    def resolve_external_ids(
        self, subject_model: str, entries: Iterable[dict], fields_chain: Sequence[str], *, required: bool = False
    ) -> tuple[dict[int, int], list[dict]]:
        """Resolve external identifiers to subject IDs."""
        entries = list(entries)
        if not entries:
            return {}, []
        if not fields_chain:
            mapped = {}
            errors: list[dict] = []
            for entry in entries:
                sid = entry.get("external_id")
                try:
                    sid_int = int(sid)
                except (TypeError, ValueError):
                    if required:
                        errors.append(
                            {
                                "index": entry.get("index"),
                                "code": "mapping_missing",
                                "message": "No mapping fields configured and subject_id missing.",
                            }
                        )
                    continue
                mapped[entry["index"]] = sid_int
            return mapped, errors

        remaining = {entry["index"]: entry.get("external_id") for entry in entries if entry.get("external_id")}
        mapped: dict[int, int] = {}
        errors: list[dict] = []
        Model = self.env[subject_model].sudo()
        for field_name in fields_chain:
            if not remaining:
                break
            values = [val for val in remaining.values() if val]
            if not values:
                break
            domain = [(field_name, "in", values)]
            if "company_id" in Model._fields:
                domain.append(("company_id", "=", self.env.company.id))
            recs = Model.search(domain)
            for rec in recs:
                ext = getattr(rec, field_name, None)
                if not ext:
                    continue
                for idx, value in list(remaining.items()):
                    if value == ext:
                        mapped[idx] = rec.id
                        remaining.pop(idx, None)
        if remaining:
            code = "mapping_missing" if required else "mapping_not_found"
            for idx, value in remaining.items():
                errors.append({"index": idx, "code": code, "message": f"No subject found for external id {value}."})
        return mapped, errors
