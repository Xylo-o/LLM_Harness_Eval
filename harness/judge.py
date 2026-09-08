from pydantic import BaseModel, Field

class Verdict(BaseModel):
    reasoning: str = Field(min_length=200)
    correctness: int = Field(ge=1, le=3)


def _remove_fence(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw.removeprefix("```json")
    elif raw.startswith("```"):
        raw = raw.removeprefix("```")
    if raw.endswith("```"):
        raw = raw.removesuffix("```")
    return(raw.strip())

