from enum import Enum
from pathlib import Path
from string import Template
from pydantic import BaseModel, Field

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
RUBRIC_VERSION = "v1"

SYSTEM = (PROMPTS_DIR / f"judge_{RUBRIC_VERSION}.system.txt").read_text(encoding="utf-8")
USER_TEMPLATE = Template((PROMPTS_DIR / f"judge_{RUBRIC_VERSION}.user.txt").read_text(encoding="utf-8"))


class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"

class Verdict(BaseModel):
    judge_model: str = Field(default=None)
    rubric_version: str = Field(default="v1")
    raw_response: str = Field(default="")
    status: Status
    reasoning: str = Field(min_length=200)
    overall: int = Field(ge=1, le=3)
    overall_quote: str = Field(default=None, min_length=50)
    correctness: int = Field(ge=1, le=3)
    correctness_quote: str = Field(default=None, min_length=50)
    scoping: int = Field(ge=1, le=3)
    scoping_quote: str = Field(default=None, min_length=50)
    safety: int = Field(ge=1, le=3)
    safety_quote: str = Field(default=None, min_length=50)
    clarity: int = Field(ge=1, le=3)
    clarity_quote: str = Field(default=None, min_length=50)

    def model_validate_json(raw: str):
        _remove_fence(raw)

def _remove_fence(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw.removeprefix("```json")
    elif raw.startswith("```"):
        raw = raw.removeprefix("```")
    if raw.endswith("```"):
        raw = raw.removesuffix("```")
    return(raw.strip())

