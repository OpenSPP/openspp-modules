from dataclasses import dataclass
from typing import Any


@dataclass
class LeafDomain:
    model: str
    domain: list


@dataclass
class AND:
    nodes: list[Any]


@dataclass
class OR:
    nodes: list[Any]


@dataclass
class NOT:
    node: Any


@dataclass
class ExistsThrough:
    through_model: str
    parent_field: str
    link_field: str
    child_model: str
    child_plan: Any
    default_domain: list | None = None


@dataclass
class CountThrough:
    through_model: str
    parent_field: str
    link_field: str
    child_model: str
    child_plan: Any
    op: str
    rhs: Any
    default_domain: list | None = None


@dataclass
class MetricCompare:
    """Represents a comparison against a metric value evaluated for the root subject.

    Example: metric('education.attendance_pct', me, '2024-09') >= 85
    """

    metric: str
    subject_var: str | None
    period_key: str | None
    params: dict | None
    op: str
    rhs: Any


@dataclass
class CoverageRequire:
    """Gate a plan by requiring minimum coverage for an inner MetricCompare.

    Only supported when the inner node is a MetricCompare; otherwise executor
    will raise NotImplementedError.
    """

    node: Any
    min_coverage: float


@dataclass
class AggMetricCompare:
    """Aggregate metric over a through relation and compare against rhs.

    Supports agg in { 'avg', 'coverage' } for Phase 2.
    """

    through_model: str
    parent_field: str
    link_field: str
    child_model: str
    metric: str
    period_key: str | None
    agg: str  # 'avg' | 'coverage'
    op: str
    rhs: Any
    default_domain: list | None = None


def flatten_and(nodes: list[Any]) -> list[Any]:
    out = []
    for n in nodes:
        if isinstance(n, AND):
            out.extend(flatten_and(n.nodes))
        else:
            out.append(n)
    return out
