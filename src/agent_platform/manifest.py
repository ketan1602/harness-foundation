from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

APPROVAL_TOOL = "human_approval"


class BudgetSpec(BaseModel):
    max_steps: int = Field(default=5, ge=1, le=100)
    max_tokens: int = Field(default=20000, ge=1)
    max_cost_usd: float = Field(default=1.0, gt=0)


class AgentManifest(BaseModel):
    agent_id: str = Field(min_length=3)
    owner: str = Field(min_length=3)
    purpose: str = Field(min_length=5)
    risk_tier: Literal["low", "medium", "high"] = "low"
    allowed_tools: list[str] = Field(default_factory=list)
    budget: BudgetSpec = Field(default_factory=BudgetSpec)

    @model_validator(mode="after")
    def require_approval_for_high_risk(self):
        if self.risk_tier == "high" and APPROVAL_TOOL not in self.allowed_tools:
            raise ValueError(f"high-risk agents require the {APPROVAL_TOOL} tool")
        return self


def load_manifest(path: str | Path) -> AgentManifest:
    return AgentManifest.model_validate(yaml.safe_load(Path(path).read_text()))
