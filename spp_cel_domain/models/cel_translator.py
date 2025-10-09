from __future__ import annotations

import logging
from typing import Any

from odoo import api, fields, models
from odoo.osv import expression

from ..services import cel_parser as P
from .cel_queryplan import (
    AND,
    NOT,
    OR,
    AggMetricCompare,
    CountThrough,
    CoverageRequire,
    ExistsThrough,
    LeafDomain,
    MetricCompare,
)

_logger = logging.getLogger(__name__)


class CelTranslator(models.AbstractModel):
    _name = "cel.translator"
    _description = "CEL Translator"

    # Entry point
    @api.model
    def translate(self, model: str, expr: str, cfg: dict[str, Any]) -> tuple[Any, str]:
        ast = P.parse(expr)
        ctx: dict[str, Any] = {"_cache": {}}
        plan, explain = self._to_plan(model, ast, cfg, ctx)
        return plan, explain

    # AST → Plan
    def _to_plan(self, model: str, node: Any, cfg: dict[str, Any], ctx: dict[str, Any]):  # noqa: C901
        if isinstance(node, P.And):
            left_plan, left_explain = self._to_plan(model, node.left, cfg, ctx)
            right_plan, right_explain = self._to_plan(model, node.right, cfg, ctx)
            return AND([left_plan, right_plan]), f"({left_explain}) AND ({right_explain})"
        if isinstance(node, P.Or):
            left_plan, left_explain = self._to_plan(model, node.left, cfg, ctx)
            right_plan, right_explain = self._to_plan(model, node.right, cfg, ctx)
            return OR([left_plan, right_plan]), f"({left_explain}) OR ({right_explain})"
        if isinstance(node, P.Not):
            neg_plan, neg_explain = self._to_plan(model, node.expr, cfg, ctx)
            negated = self._negate_leaf(neg_plan)
            if negated is not None:
                return negated, f"NOT ({neg_explain})"
            return NOT(neg_plan), f"NOT ({neg_explain})"
        if isinstance(node, P.Compare):
            return self._cmp_to_leaf(model, node, cfg, ctx)
        if isinstance(node, P.InOp):
            left_field, left_model = self._resolve_field(model, node.left, cfg, ctx)
            vals = [v for v in node.items]
            domain = [(left_field, "in", vals)]
            return LeafDomain(left_model or model, domain), f"{left_field} IN {vals}"
        if isinstance(node, P.Call):
            # all_over(collection, metric(...) <op> rhs)
            if isinstance(node.func, P.Ident) and node.func.name == "all_over":
                if (
                    len(node.args) < 2
                    or not isinstance(node.args[0], P.Ident)
                    or not isinstance(node.args[1], P.Compare)
                ):
                    raise NotImplementedError("all_over requires (relation_symbol, metric(...) <op> rhs)")
                coll_name = node.args[0].name
                inner_cmp = node.args[1]
                # Support metric() or namespaced metric function on left
                metric_name = None
                period_key = None
                left = inner_cmp.left
                if isinstance(left, P.Call) and isinstance(left.func, P.Ident) and left.func.name == "metric":
                    metric_name = self._eval_literal(left.args[0], ctx) if left.args else None
                    if len(left.args) >= 3:
                        period_key = self._eval_literal(left.args[2], ctx)
                        if not isinstance(period_key, str | int):
                            period_key = str(period_key)
                elif isinstance(left, P.Call) and isinstance(left.func, P.Attr):
                    # Dotted metric function like education.attendance_pct(period?)
                    def _flatten_attr(a):
                        parts = []
                        cur = a
                        while isinstance(cur, P.Attr):
                            parts.append(cur.name)
                            cur = cur.obj
                        if isinstance(cur, P.Ident):
                            parts.append(cur.name)
                        return ".".join(reversed(parts))

                    metric_name = _flatten_attr(left.func)
                    if left.args:
                        pk = self._eval_literal(left.args[0], ctx)
                        if not isinstance(pk, dict | list):
                            period_key = pk
                else:
                    raise NotImplementedError(
                        "all_over currently supports only metric() or namespaced metric() on the left side"
                    )
                sym = cfg.get("symbols", {}).get(coll_name)
                if not (sym and sym.get("relation") == "rel"):
                    raise NotImplementedError("all_over only supports relation symbols (through models)")
                child_model = self._symbol_child_model(sym)
                through = sym["through"]
                parent_field = sym["parent"]
                link_field = sym.get("link_to") or sym.get("link_field") or sym.get("link") or "id"
                default_domain = sym.get("default_domain")
                op = {"EQ": "==", "NE": "!=", "GT": ">", "GE": ">=", "LT": "<", "LE": "<="}[inner_cmp.op]
                rhs = self._eval_literal(inner_cmp.right, ctx)
                node_plan = AggMetricCompare(
                    through_model=through,
                    parent_field=parent_field,
                    link_field=link_field,
                    child_model=child_model,
                    metric=metric_name,
                    period_key=str(period_key) if period_key is not None else None,
                    agg="all",
                    op=op,
                    rhs=rhs,
                    default_domain=default_domain,
                )
                return node_plan, f"ALL over {coll_name} of METRIC({metric_name}) {op} {rhs}"
            # require_coverage(inner_expr, min)
            if isinstance(node.func, P.Ident) and node.func.name == "require_coverage":
                inner = node.args[0] if node.args else None
                minv = float(self._eval_literal(node.args[1], ctx)) if len(node.args) > 1 else 0.8
                inner_plan, inner_explain = self._to_plan(model, inner, cfg, ctx)
                return CoverageRequire(inner_plan, minv), f"REQUIRE_COVERAGE({minv}): {inner_explain}"
            # Check function registry first (for extensibility)
            if isinstance(node.func, P.Ident):
                func_name = node.func.name
                try:
                    registry = self.env["cel.function.registry"]
                    if registry.is_registered(func_name):
                        handler = registry.get_handler(func_name)
                        if handler:
                            # Evaluate arguments
                            args = [self._eval_literal(arg, ctx) for arg in node.args]
                            try:
                                result = handler(*args)
                                # For now, treat registry functions as boolean filters
                                # TODO: Support more complex return types
                                if isinstance(result, bool):
                                    if result:
                                        return LeafDomain(model, [("id", "!=", 0)]), f"{func_name}({args})=True"
                                    else:
                                        return LeafDomain(model, [("id", "=", 0)]), f"{func_name}({args})=False"
                                else:
                                    # Return value as constant for now
                                    return LeafDomain(model, [("id", "!=", 0)]), f"{func_name}({args})={result}"
                            except Exception as e:
                                _logger.warning(
                                    f"[CEL Translator] Error executing registered function '{func_name}': {e}"
                                )
                except Exception:
                    pass  # Registry not available or function check failed, continue to built-ins

            # Method-style EXISTS/COUNT: members.exists(var, pred)
            if isinstance(node.func, P.Attr) and isinstance(node.func.obj, P.Ident):
                coll_name = node.func.obj.name
                method = node.func.name
                sym = cfg.get("symbols", {}).get(coll_name)
                if sym and sym.get("relation") == "rel" and method in ("exists", "count"):
                    var = node.args[0]
                    pred = node.args[1] if len(node.args) > 1 else P.Literal(True)
                    child_model = self._symbol_child_model(sym)
                    subctx = dict(ctx)
                    if isinstance(var, P.Ident):
                        subctx[var.name] = {"kind": "rel_var", "sym": sym, "model": child_model}
                    child_plan, explain = self._to_plan(child_model, pred, cfg, subctx)
                    through = sym["through"]
                    parent_field = sym["parent"]
                    link_field = sym.get("link_to") or sym.get("link_field") or sym.get("link") or "id"
                    default_domain = sym.get("default_domain")
                    if method == "exists":
                        return (
                            ExistsThrough(through, parent_field, link_field, child_model, child_plan, default_domain),
                            f"EXISTS in {coll_name}: {explain}",
                        )
                    else:
                        # count(...) must be compared later; represent as count == True unsupported alone
                        return CountThrough(
                            through, parent_field, link_field, child_model, child_plan, ">=", 1, default_domain
                        ), f"COUNT in {coll_name}: {explain}"
                elif method in ("exists", "count"):
                    # User tried to use exists/count on unknown or invalid symbol
                    raise KeyError(coll_name)
            # Function-style EXISTS/COUNT: exists(collection, var, pred) / count(collection, var, pred)
            if isinstance(node.func, P.Ident) and node.func.name in ("exists", "count"):
                if len(node.args) >= 2 and isinstance(node.args[0], P.Ident):
                    coll_name = node.args[0].name
                    var = node.args[1]
                    pred = node.args[2] if len(node.args) > 2 else P.Literal(True)
                    sym = cfg.get("symbols", {}).get(coll_name)
                    if sym and sym.get("relation") == "rel":
                        child_model = self._symbol_child_model(sym)
                        subctx = dict(ctx)
                        if isinstance(var, P.Ident):
                            subctx[var.name] = {"kind": "rel_var", "sym": sym, "model": child_model}
                        child_plan, explain = self._to_plan(child_model, pred, cfg, subctx)
                        through = sym["through"]
                        parent_field = sym["parent"]
                        link_field = sym.get("link_to") or sym.get("link_field") or sym.get("link") or "id"
                        default_domain = sym.get("default_domain")
                        if node.func.name == "exists":
                            return (
                                ExistsThrough(
                                    through, parent_field, link_field, child_model, child_plan, default_domain
                                ),
                                f"EXISTS in {coll_name}: {explain}",
                            )
                        else:
                            return (
                                CountThrough(
                                    through, parent_field, link_field, child_model, child_plan, ">=", 1, default_domain
                                ),
                                f"COUNT in {coll_name}: {explain}",
                            )
                    else:
                        # Unknown or invalid symbol in function-style exists/count
                        raise KeyError(coll_name)
            # Simple leaf function: head(m), has_role(m,"name") -> boolean on membership kinds
            if isinstance(node.func, P.Ident) and node.func.name in ("head", "has_role"):
                m = node.args[0]
                role_names = None
                role_ids = None
                if node.func.name == "has_role" and len(node.args) > 1:
                    hint = self._eval_literal(node.args[1], ctx)
                    if isinstance(hint, dict):
                        role_names = hint.get("names") or role_names
                        role_ids = hint.get("ids") or role_ids
                    elif isinstance(hint, str):
                        role_names = [hint]
                    elif isinstance(hint, int):
                        role_ids = [hint]
                elif node.func.name == "head":
                    role_names = cfg.get("roles", {}).get("head", ["Head"])
                field, mdl = self._resolve_field(model, P.Attr(P.Attr(m, "_link"), "kind"), cfg, ctx)
                domain: list[Any] = []
                if role_ids:
                    domain.append((field, "in", role_ids))
                elif role_names:
                    domain.append((field + ".name", "in", role_names))
                else:
                    domain.append((field, "!=", False))
                return LeafDomain(mdl or model, domain), f"membership has role in {role_names or role_ids}"
            # contains(field, "text")
            if isinstance(node.func, P.Ident) and node.func.name == "contains":
                field, mdl = self._resolve_field(model, node.args[0], cfg, ctx)
                val = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], P.Literal) else ""
                return LeafDomain(mdl or model, [(field, "ilike", val)]), f"{field} ILIKE {val}"
            if isinstance(node.func, P.Ident) and node.func.name == "startswith":
                field, mdl = self._resolve_field(model, node.args[0], cfg, ctx)
                prefix = self._eval_literal(node.args[1], ctx) if len(node.args) > 1 else ""
                if not isinstance(prefix, str):
                    prefix = str(prefix or "")
                return LeafDomain(mdl or model, [(field, "ilike", f"{prefix}%")]), f"{field} startswith {prefix}"
            if isinstance(node.func, P.Ident) and node.func.name == "between" and len(node.args) >= 3:
                ge = P.Compare("GE", node.args[0], node.args[1])
                le = P.Compare("LE", node.args[0], node.args[2])
                gp, ge_text = self._to_plan(model, ge, cfg, ctx)
                lp, le_text = self._to_plan(model, le, cfg, ctx)
                if isinstance(gp, LeafDomain) and isinstance(lp, LeafDomain) and gp.model == lp.model:
                    dom_terms: list[Any] = []
                    for leaf in (gp, lp):
                        current = leaf.domain or []
                        if current and isinstance(current[0], str) and current[0] in ("&", "|"):
                            dom_terms.extend(current[1:])
                        else:
                            dom_terms.extend(current)
                    combined = dom_terms
                    if len(dom_terms) > 1:
                        combined = ["&", *dom_terms]
                    return LeafDomain(gp.model, combined), f"({ge_text}) AND ({le_text})"
                return AND([gp, lp]), f"({ge_text}) AND ({le_text})"
            if isinstance(node.func, P.Ident) and node.func.name == "has_tag":
                tag_value = self._eval_literal(node.args[0], ctx) if node.args else ""
                if isinstance(tag_value, list | tuple):
                    tag_value = tag_value[0] if tag_value else ""
                if not isinstance(tag_value, str):
                    tag_value = str(tag_value or "")
                return LeafDomain(model, [("category_id.name", "ilike", tag_value)]), f"has tag ILIKE {tag_value}"
            # program("Name") returns program id
            if isinstance(node.func, P.Ident) and node.func.name == "program":
                name = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else None
                pid = None
                if name:
                    rec = self.env["g2p.program"].search([("name", "=", name)], limit=1)
                    pid = rec.id or None
                return LeafDomain(model, [("id", "!=", 0)]), f"PROGRAM({name})={pid}"
        # Boolean field used as predicate (e.g., m._link.is_ended)
        if isinstance(node, P.Attr | P.Ident):
            fld, mdl = self._resolve_field(model, node, cfg, ctx)
            try:
                ft = self.env[mdl]._fields.get(fld)
                if ft and getattr(ft, "type", None) == "boolean":
                    return LeafDomain(mdl or model, [(fld, "=", True)]), f"{fld} is True"
            except Exception:
                pass
        # Fallback: treat as True (no-op)
        return LeafDomain(model, [("id", "!=", 0)]), "TRUE"

    def _cmp_to_leaf(self, model: str, cmp: P.Compare, cfg: dict[str, Any], ctx: dict[str, Any]):  # noqa: C901
        opmap = {"EQ": "=", "NE": "!=", "GT": ">", "GE": ">=", "LT": "<", "LE": "<="}
        # Rewrite age_years(field) <op> N into date comparisons
        if isinstance(cmp.left, P.Call) and isinstance(cmp.left.func, P.Ident) and cmp.left.func.name == "age_years":
            fld, mdl = self._resolve_field(model, cmp.left.args[0], cfg, ctx)
            from ..services.cel_functions import years_ago

            n = cmp.right.value if isinstance(cmp.right, P.Literal) else 0
            # cutoff_n is date(today - n years)
            cutoff_n = years_ago(n)
            op = cmp.op  # 'LT','LE','GT','GE','EQ','NE'
            domain = []
            explain = ""
            if op == "LT":
                # age < n  => birthdate > today - n years (younger than n)
                domain = [(fld, ">", cutoff_n)]
                explain = f"{fld} > today - {n}y"
            elif op == "LE":
                # age <= n => birthdate >= today - n years
                domain = [(fld, ">=", cutoff_n)]
                explain = f"{fld} >= today - {n}y"
            elif op == "GT":
                # age > n  => birthdate < today - n years (older than n)
                domain = [(fld, "<", cutoff_n)]
                explain = f"{fld} < today - {n}y"
            elif op == "GE":
                # age >= n => birthdate <= today - n years
                domain = [(fld, "<=", cutoff_n)]
                explain = f"{fld} <= today - {n}y"
            elif op == "EQ":
                # age == n => (today-(n+1)y, today-n y]
                cutoff_high = years_ago(n)
                cutoff_low = years_ago(n + 1)
                domain = ["&", (fld, ">", cutoff_low), (fld, "<=", cutoff_high)]
                explain = f"{fld} in (today - {n+1}y, today - {n}y]"
            elif op == "NE":
                # age != n => birthdate <= today-(n+1)y OR birthdate > today-n y
                cutoff_high = years_ago(n)
                cutoff_low = years_ago(n + 1)
                domain = ["|", (fld, "<=", cutoff_low), (fld, ">", cutoff_high)]
                explain = f"{fld} <= today - {n+1}y OR {fld} > today - {n}y"
            return LeafDomain(mdl or model, domain), explain
        # Metric(metric_name, subject, period_key?) <op> value
        if isinstance(cmp.left, P.Call) and (
            (isinstance(cmp.left.func, P.Ident) and cmp.left.func.name == "metric") or isinstance(cmp.left.func, P.Attr)
        ):
            # metric("name", subject?, period?) OR namespaced metric function
            if isinstance(cmp.left.func, P.Ident) and cmp.left.func.name == "metric":
                metric_name = self._eval_literal(cmp.left.args[0], ctx) if cmp.left.args else None
                subject_var = None
                if len(cmp.left.args) >= 2:
                    if isinstance(cmp.left.args[1], P.Ident):
                        subject_var = cmp.left.args[1].name
                    elif isinstance(cmp.left.args[1], P.Attr) and isinstance(cmp.left.args[1].obj, P.Ident):
                        subject_var = cmp.left.args[1].obj.name
                period_key = None
                if len(cmp.left.args) >= 3:
                    period_key = self._eval_literal(cmp.left.args[2], ctx)
                    if not isinstance(period_key, str | int):
                        period_key = str(period_key)
            else:
                # namespaced function: first arg period?, second subject?
                def _flatten_attr(a):
                    parts = []
                    cur = a
                    while isinstance(cur, P.Attr):
                        parts.append(cur.name)
                        cur = cur.obj
                    if isinstance(cur, P.Ident):
                        parts.append(cur.name)
                    return ".".join(reversed(parts))

                metric_name = _flatten_attr(cmp.left.func)
                subject_var = None
                period_key = None
                if cmp.left.args:
                    p0 = self._eval_literal(cmp.left.args[0], ctx)
                    if not isinstance(p0, dict | list):
                        period_key = p0
                if len(cmp.left.args) >= 2:
                    a1 = cmp.left.args[1]
                    if isinstance(a1, P.Ident):
                        subject_var = a1.name
                    elif isinstance(a1, P.Attr) and isinstance(a1.obj, P.Ident):
                        subject_var = a1.obj.name
            rhs = self._eval_literal(cmp.right, ctx)
            op = {"EQ": "==", "NE": "!=", "GT": ">", "GE": ">=", "LT": "<", "LE": "<="}[cmp.op]
            plan = MetricCompare(
                metric=metric_name, subject_var=subject_var, period_key=period_key, params=None, op=op, rhs=rhs
            )
            return plan, f"METRIC({metric_name}) {op} {rhs}"
        # Count(...) comparison
        if isinstance(cmp.left, P.Call) and isinstance(cmp.left.func, P.Ident) and cmp.left.func.name == "count":
            if len(cmp.left.args) >= 2 and isinstance(cmp.left.args[0], P.Ident):
                coll_name = cmp.left.args[0].name
                var = cmp.left.args[1]
                pred = cmp.left.args[2] if len(cmp.left.args) > 2 else P.Literal(True)
                sym = cfg.get("symbols", {}).get(coll_name)
                if sym and sym.get("relation") == "rel":
                    child_model = self._symbol_child_model(sym)
                    subctx = dict(ctx)
                    if isinstance(var, P.Ident):
                        subctx[var.name] = {"kind": "rel_var", "sym": sym, "model": child_model}
                    child_plan, explain = self._to_plan(child_model, pred, cfg, subctx)
                    through = sym["through"]
                    parent_field = sym["parent"]
                    link_field = sym.get("link_to") or sym.get("link_field") or sym.get("link") or "id"
                    default_domain = sym.get("default_domain")
                    rhs = self._eval_literal(cmp.right, ctx)
                    return (
                        CountThrough(
                            through,
                            parent_field,
                            link_field,
                            child_model,
                            child_plan,
                            {"EQ": "==", "NE": "!=", "GT": ">", "GE": ">=", "LT": "<", "LE": "<="}[cmp.op],
                            rhs,
                            default_domain,
                        ),
                        f"COUNT in {coll_name} {cmp.op} {rhs}: {explain}",
                    )

        # Aggregators over collections: avg_over/coverage_over/counted all_over
        if (
            isinstance(cmp.left, P.Call)
            and isinstance(cmp.left.func, P.Ident)
            and cmp.left.func.name in ("avg_over", "coverage_over", "all_over")
        ):
            agg = (
                "avg"
                if cmp.left.func.name == "avg_over"
                else ("coverage" if cmp.left.func.name == "coverage_over" else "all")
            )
            if len(cmp.left.args) < 2 or not isinstance(cmp.left.args[0], P.Ident):
                raise NotImplementedError(f"{agg}_over requires a relation symbol and a metric() call in Phase 2")
            coll_name = cmp.left.args[0].name
            inner = cmp.left.args[1]
            # Support metric() or namespaced function inside
            metric_name = None
            period_key = None
            if isinstance(inner, P.Call) and isinstance(inner.func, P.Ident) and inner.func.name == "metric":
                metric_name = self._eval_literal(inner.args[0], ctx) if inner.args else None
                if len(inner.args) >= 3:
                    period_key = self._eval_literal(inner.args[2], ctx)
                    if not isinstance(period_key, str | int):
                        period_key = str(period_key)
            elif isinstance(inner, P.Call) and isinstance(inner.func, P.Attr):

                def _flatten_attr(a):
                    parts = []
                    cur = a
                    while isinstance(cur, P.Attr):
                        parts.append(cur.name)
                        cur = cur.obj
                    if isinstance(cur, P.Ident):
                        parts.append(cur.name)
                    return ".".join(reversed(parts))

                metric_name = _flatten_attr(inner.func)
                if inner.args:
                    pk = self._eval_literal(inner.args[0], ctx)
                    if not isinstance(pk, dict | list):
                        period_key = pk
            else:
                raise NotImplementedError(f"{agg}_over currently supports only metric() or namespaced metric() inside")
            sym = cfg.get("symbols", {}).get(coll_name)
            if not (sym and sym.get("relation") == "rel"):
                raise NotImplementedError(f"{agg}_over only supports relation symbols (through models)")
            child_model = self._symbol_child_model(sym)
            through = sym["through"]
            parent_field = sym["parent"]
            link_field = sym.get("link_to") or sym.get("link_field") or sym.get("link") or "id"
            default_domain = sym.get("default_domain")
            rhs = self._eval_literal(cmp.right, ctx)
            op = {"EQ": "==", "NE": "!=", "GT": ">", "GE": ">=", "LT": "<", "LE": "<="}[cmp.op]
            node = AggMetricCompare(
                through_model=through,
                parent_field=parent_field,
                link_field=link_field,
                child_model=child_model,
                metric=metric_name,
                period_key=str(period_key) if period_key is not None else None,
                agg=agg,
                op=op,
                rhs=rhs,
                default_domain=default_domain,
            )
            return node, f"{agg.upper()} over {coll_name} of METRIC({metric_name}) {op} {rhs}"

        # Normal comparison
        left_field, left_model = self._resolve_field(model, cmp.left, cfg, ctx)
        # normalize aliases
        left_field = self._normalize_field_name(left_model or model, left_field)
        right = self._eval_literal(cmp.right, ctx)
        dom = self._smart_op_domain(left_field, opmap[cmp.op], right, left_model or model)
        return LeafDomain(left_model or model, dom), f"{left_field} {opmap[cmp.op]} {right}"

    def _eval_literal(self, node: Any, ctx: dict[str, Any] | None = None):  # noqa: C901
        cache = None
        if ctx is not None:
            cache = ctx.setdefault("_cache", {})
        if isinstance(node, P.Literal):
            return node.value
        if isinstance(node, P.Call) and isinstance(node.func, P.Ident):
            if node.func.name == "program":
                name = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else None
                if not name:
                    return 0
                cache_key = ("program", name)
                if cache is not None and cache_key in cache:
                    return cache[cache_key]
                rec = self.env["g2p.program"].search([("name", "=", name)], limit=1)
                pid = rec.id or 0
                if cache is not None:
                    cache[cache_key] = pid
                return pid
            if node.func.name == "date":
                from datetime import date as _date

                s = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else None
                try:
                    return _date.fromisoformat(s)
                except Exception:
                    return s
            if node.func.name == "today":
                return fields.Date.context_today(self)
            if node.func.name == "now":
                return fields.Datetime.now()
            # cycle helpers implemented above (cycle/last_cycle/first_cycle/previous/next)
            if node.func.name == "previous":
                arg = node.args[0] if node.args else None
                key = None
                if arg is not None:
                    if isinstance(arg, P.Literal):
                        key = arg.value
                    else:
                        key = self._eval_literal(arg, ctx)
                if isinstance(key, str) and key.startswith("cycle:"):
                    try:
                        cid = int(key.split(":", 1)[1])
                    except Exception:
                        return key
                    cyc = self.env["g2p.cycle"].browse(cid)
                    prev = self.env["g2p.cycle"].search(
                        [("program_id", "=", cyc.program_id.id), ("sequence", "<", cyc.sequence)],
                        order="sequence desc",
                        limit=1,
                    )
                    return f"cycle:{prev.id}" if prev else key
                return key
            if node.func.name == "next":
                arg = node.args[0] if node.args else None
                key = None
                if arg is not None:
                    if isinstance(arg, P.Literal):
                        key = arg.value
                    else:
                        key = self._eval_literal(arg, ctx)
                if isinstance(key, str) and key.startswith("cycle:"):
                    try:
                        cid = int(key.split(":", 1)[1])
                    except Exception:
                        return key
                    cyc = self.env["g2p.cycle"].browse(cid)
                    nxt = self.env["g2p.cycle"].search(
                        [("program_id", "=", cyc.program_id.id), ("sequence", ">", cyc.sequence)],
                        order="sequence asc",
                        limit=1,
                    )
                    return f"cycle:{nxt.id}" if nxt else key
                return key
            if node.func.name == "cycle":
                prog_name = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else None
                cyc_name = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], P.Literal) else None
                if not prog_name or not cyc_name:
                    return None
                cache_key = ("cycle", prog_name, cyc_name)
                if cache is not None and cache_key in cache:
                    return cache[cache_key]
                prog = self.env["g2p.program"].search([("name", "=", prog_name)], limit=1)
                cyc = self.env["g2p.cycle"].search([("program_id", "=", prog.id), ("name", "=", cyc_name)], limit=1)
                cid = f"cycle:{cyc.id}" if cyc else None
                if cache is not None:
                    cache[cache_key] = cid
                return cid
            if node.func.name == "last_cycle":
                prog_name = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else None
                if not prog_name:
                    return None
                cache_key = ("last_cycle", prog_name)
                if cache is not None and cache_key in cache:
                    return cache[cache_key]
                prog = self.env["g2p.program"].search([("name", "=", prog_name)], limit=1)
                cyc = self.env["g2p.cycle"].search([("program_id", "=", prog.id)], order="sequence desc", limit=1)
                cid = f"cycle:{cyc.id}" if cyc else None
                if cache is not None:
                    cache[cache_key] = cid
                return cid
            if node.func.name == "first_cycle":
                prog_name = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else None
                if not prog_name:
                    return None
                cache_key = ("first_cycle", prog_name)
                if cache is not None and cache_key in cache:
                    return cache[cache_key]
                prog = self.env["g2p.program"].search([("name", "=", prog_name)], limit=1)
                cyc = self.env["g2p.cycle"].search([("program_id", "=", prog.id)], order="sequence asc", limit=1)
                cid = f"cycle:{cyc.id}" if cyc else None
                if cache is not None:
                    cache[cache_key] = cid
                return cid
            if node.func.name == "kind":
                name = node.args[0].value if node.args and isinstance(node.args[0], P.Literal) else None
                if name:
                    cache_key = ("kind", name)
                    if cache is not None and cache_key in cache:
                        return cache[cache_key]
                    rec = self.env["g2p.group.membership.kind"].search([("name", "=", name)], limit=1)
                    if rec:
                        result = {"ids": [rec.id], "names": [rec.name]}
                        if cache is not None:
                            cache[cache_key] = result
                        return result
                return {"ids": None, "names": [name] if name else None}
        return node

    def _smart_op_domain(self, field: str, op: str, right: Any, model_name: str) -> list[Any]:  # noqa: C901
        # If the user already targeted a dotted subfield, keep it literal
        if "." in field:
            return [(field, op, right)]
        # Try to be helpful with many2one/many2many comparisons using a human label field
        try:
            ft = self.env[model_name]._fields.get(field)
            if ft and getattr(ft, "type", None) in ("many2one", "many2many") and op in ("=", "ilike", "in"):
                # Detect a reasonable label field on the comodel (prefer 'value', then 'name', then 'code')
                label_field = "name"
                comodel = getattr(ft, "comodel_name", None)
                if comodel:
                    cfields = self.env[comodel]._fields
                    for cand in ("value", "name", "code"):
                        if cand in cfields:
                            label_field = cand
                            break
                resolved_ids: list[int] = []
                if comodel and isinstance(right, str):
                    if "value" in self.env[comodel]._fields:
                        direct = (
                            self.env[comodel]
                            .with_context(active_test=False)
                            .search([("value", "=", right.capitalize())], limit=None)
                        )
                        if not direct and right.lower() in {"male", "female"}:
                            code_defaults = {"male": "M", "female": "F"}
                            direct = (
                                self.env[comodel]
                                .with_context(active_test=False)
                                .sudo()
                                .create(
                                    {
                                        "value": right.capitalize(),
                                        "code": code_defaults[right.lower()],
                                    }
                                )
                            )
                        if direct:
                            resolved_ids = direct.ids
                            if op in ("=", "=="):
                                if len(resolved_ids) == 1:
                                    return [(field, "=", resolved_ids[0])]
                                return [(field, "in", resolved_ids)]
                            if op == "in":
                                return [(field, "in", resolved_ids)]
                            if op == "ilike":
                                base_domain = [(field, "in", resolved_ids)]
                                return expression.OR([base_domain, [(f"{field}.{label_field}", "ilike", right)]])

                    name_clauses: list[list[Any]] = []
                    for attr in ("value", "name", "code"):
                        if attr in self.env[comodel]._fields:
                            name_clauses.append([(attr, "ilike", right)])
                    lookup_domain: list[Any]
                    if name_clauses:
                        lookup_domain = expression.OR(name_clauses)
                    else:
                        lookup_domain = [("name", "ilike", right)]
                    matches = self.env[comodel].with_context(active_test=False).search(lookup_domain, limit=None)
                    try:
                        _logger.info(
                            "[CEL TRANSLATOR] smart-op lookup model=%s field=%s op=%s value=%s matches=%s",
                            model_name,
                            field,
                            op,
                            right,
                            [(m.id, getattr(m, "value", None), getattr(m, "name", None)) for m in matches],
                        )
                    except Exception:
                        pass
                    if matches:
                        target = right.casefold()
                        exact = matches.filtered(
                            lambda rec: any(
                                isinstance(getattr(rec, attr, None), str) and getattr(rec, attr).casefold() == target
                                for attr in ("value", "name", "code")
                            )
                        )
                        resolved_ids = exact.ids if exact else []
                if resolved_ids:
                    if op in ("=", "=="):
                        if len(resolved_ids) == 1:
                            return [(field, "=", resolved_ids[0])]
                        return [(field, "in", resolved_ids)]
                    if op == "in":
                        return [(field, "in", resolved_ids)]
                    if op == "ilike":
                        base_domain = [(field, "in", resolved_ids)]
                        label_domain = [(f"{field}.{label_field}", "ilike", right)]
                        return expression.OR([base_domain, label_domain])
                if isinstance(right, str):
                    if op in ("=", "=="):
                        return [(f"{field}.{label_field}", "=", right)]
                    if op == "ilike":
                        return [(f"{field}.{label_field}", "ilike", right)]
                return [(field, op, right)]
        except Exception:
            # Fallback to raw domain
            pass
        return [(field, op, right)]

    def _resolve_field(self, model: str, expr: Any, cfg: dict[str, Any], ctx: dict[str, Any]):
        # Ident 'me' or variable field chains
        if isinstance(expr, P.Attr):
            # handle m._link.<field> → membership model fields
            if isinstance(expr.obj, P.Attr) and isinstance(expr.obj.obj, P.Ident) and expr.obj.name == "_link":
                var = expr.obj.obj.name
                var_info = ctx.get(var, {})
                sym = var_info.get("sym", {})
                through_model = sym.get("through")
                return self._normalize_field_name(through_model, expr.name), through_model
            left_field, left_model = self._resolve_field(model, expr.obj, cfg, ctx)
            # simple attr: concatenate with dot path for m2o name matching later
            if left_field:
                fld = expr.name if left_field == "id" else f"{left_field}.{expr.name}"
                return self._normalize_field_name(left_model or model, fld), left_model or model
            return self._normalize_field_name(left_model or model, expr.name), left_model or model
        if isinstance(expr, P.Ident):
            if expr.name == "me":
                return "id", model
            # variable refers to child record; start from its model
            var_info = ctx.get(expr.name)
            if var_info:
                return "id", var_info.get("model", model)
            # plain identifier -> field on current model
            return expr.name, model
        if isinstance(expr, P.Literal):
            return expr.value, model
        return "id", model

    def _symbol_child_model(self, sym: dict[str, Any]) -> str:
        return sym.get("child_model") or "res.partner"

    def _normalize_field_name(self, model: str, field: str) -> str:
        # Map friendly names to real fields for key models
        if model in ("g2p.program_membership", "g2p.entitlement"):
            field = field.replace(".program", ".program_id")
            if field == "program":
                return "program_id"
        # Allow omitting _id suffix for many2one fields (e.g., district -> district_id)
        if "." not in field and model:
            try:
                model_fields = self.env[model]._fields
                alt = f"{field}_id"
                if field not in model_fields and alt in model_fields:
                    return alt
            except Exception:
                pass
        return field

    def _negate_leaf(self, plan):
        if not isinstance(plan, LeafDomain):
            return None
        domain = plan.domain
        if isinstance(domain, list) and domain and isinstance(domain[0], tuple):
            field, op, value = domain[0]
            if op == "=" and isinstance(value, bool):
                return LeafDomain(plan.model, [(field, "=", not value)])
            if op == "!=" and isinstance(value, bool):
                return LeafDomain(plan.model, [(field, "=", value)])
            if op == "!=" and value == "":
                return LeafDomain(plan.model, ["|", (field, "=", False), (field, "=", "")])
            if op == "=" and value == "":
                return LeafDomain(plan.model, ["&", (field, "!=", False), (field, "!=", "")])
        return None
