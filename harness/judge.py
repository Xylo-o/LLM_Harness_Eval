from pydantic import BaseModel, Field

class Verdict(BaseModel):
    reasoning: str = Field(min_length=200)

    overall: int = Field(ge=1, le=3)
    overall_quote: str | None = Field(default=None, min_length=50)

    correctness: int = Field(ge=1, le=3)
    correctness_quote: str | None = Field(default=None, min_length=50)

    scoping: int = Field(ge=1, le=3)
    scoping_quote: str | None = Field(default=None, min_length=50)

    safety: int = Field(ge=1, le=3)
    safety_quote: str | None = Field(default=None, min_length=50)

    clarity: int = Field(ge=1, le=3)
    clarity_quote: str | None = Field(default=None, min_length=50)


def _remove_fence(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw.removeprefix("```json")
    elif raw.startswith("```"):
        raw = raw.removeprefix("```")
    if raw.endswith("```"):
        raw = raw.removesuffix("```")
    return(raw.strip())

def parse_json(output: str):
    _remove_fence(output)