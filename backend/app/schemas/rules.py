from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


RuleOp = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "nin",
    "contains",
    "regex",
    "exists",
]


class Rule(BaseModel):
    """
    Generic rule definition.
    All behavior is user-configurable by storing these documents in MongoDB.
    """

    name: str
    enabled: bool = True
    target_path: str = Field(..., description="Dot-path into the job/client payload (e.g. client.rating)")
    op: RuleOp
    value: Optional[Any] = None
    weight: Optional[float] = Field(default=None, description="Optional scoring weight")
    required: bool = Field(default=False, description="If true and rule fails -> fail job")
    metadata: dict[str, Any] = Field(default_factory=dict)


class RulesetUpsert(BaseModel):
    """
    Rulesets for client/job/risk scoring & filtering.
    """

    enabled: bool = True
    rules: list[Rule] = Field(default_factory=list)
    aggregation: Literal["sum", "avg", "max", "min"] = "sum"
    metadata: dict[str, Any] = Field(default_factory=dict)


class RulesetOut(BaseModel):
    id: str
    enabled: bool
    rules: list[Rule]
    aggregation: str
    metadata: dict[str, Any]


