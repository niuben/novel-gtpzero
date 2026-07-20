from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1)
    enabled_rule_ids: list[str] | None = None


class RuleOption(BaseModel):
    rule_id: str
    name: str
    description: str
    action: str
    risk: str


class Change(BaseModel):
    rule_id: str
    type: str
    before: str
    after: str | None = None
    reason: str


class Tip(BaseModel):
    rule_id: str
    match: str
    message: str
    risk: str


class LineResult(BaseModel):
    line_id: str
    index: int
    original_text: str
    suggested_text: str
    final_text: str
    changed: bool
    changes: list[Change]
    tips: list[Tip]
    status: str = "processed"


class ProcessResponse(BaseModel):
    lines: list[LineResult]
    final_text: str
