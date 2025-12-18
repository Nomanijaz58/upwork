import re
from dataclasses import dataclass
from typing import Any, Optional

from ..schemas.rules import Rule, RuleOp


def get_path(payload: dict[str, Any], path: str) -> Any:
    """
    Dot-path lookup into dict payload.
    """
    cur: Any = payload
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        if part not in cur:
            return None
        cur = cur[part]
    return cur


@dataclass
class RuleEval:
    rule: Rule
    passed: bool
    actual: Any
    reason: Optional[str] = None


def eval_rule(rule: Rule, payload: dict[str, Any]) -> RuleEval:
    actual = get_path(payload, rule.target_path)
    op: RuleOp = rule.op
    expected = rule.value

    passed = True
    reason = None

    try:
        if op == "exists":
            passed = actual is not None
        elif op == "eq":
            passed = actual == expected
        elif op == "ne":
            passed = actual != expected
        elif op == "gt":
            passed = actual is not None and expected is not None and actual > expected
        elif op == "gte":
            passed = actual is not None and expected is not None and actual >= expected
        elif op == "lt":
            passed = actual is not None and expected is not None and actual < expected
        elif op == "lte":
            passed = actual is not None and expected is not None and actual <= expected
        elif op == "in":
            passed = actual in (expected or [])
        elif op == "nin":
            passed = actual not in (expected or [])
        elif op == "contains":
            if actual is None:
                passed = False
            elif isinstance(actual, str):
                passed = str(expected).lower() in actual.lower()
            elif isinstance(actual, list):
                passed = expected in actual
            else:
                passed = False
        elif op == "regex":
            if actual is None:
                passed = False
            else:
                passed = re.search(str(expected), str(actual)) is not None
        else:
            passed = False
            reason = f"Unsupported op: {op}"
    except Exception as e:
        passed = False
        reason = f"Rule eval error: {e}"

    if not passed and reason is None:
        reason = f"Rule '{rule.name}' failed: {rule.target_path} {rule.op} {expected!r} (actual={actual!r})"

    return RuleEval(rule=rule, passed=passed, actual=actual, reason=reason)


def aggregate(values: list[float], mode: str) -> float:
    if not values:
        return 0.0
    if mode == "avg":
        return sum(values) / len(values)
    if mode == "max":
        return max(values)
    if mode == "min":
        return min(values)
    # default: sum
    return sum(values)


