from dataclasses import dataclass
from .providers import OpenAIProvider
from .scorers import SCORERS

@dataclass
class CaseResult:
    case_key: str
    prompt: str
    scorer_config: list
    response: str | None = None
    latency_ms: int | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    error: str | None = None
    scores: list = field(default_factory=list)

@dataclass
class ScoreResult:
    scorer_name: str
    passed: bool
    detail: dict


def runner(suite: str, model: str):
    provider = OpenAIProvider(model=model)
    results = []
    scores = []
    for case in suite.cases:
        error = ""
        try:
            response = provider.complete(case.prompt)
        except Exception as e:
            error = str(e)
            response.text = ""
            continue
        for cfg in case.scorers:
            passed, detail = SCORERS[cfg["type"]](response.text, cfg)
            scores.append(passed, detail)
        results.append(CaseResult(case_key=case.id, response=response.text, latency_ms=response.latency_ms, tokens_in=response.tokens_in, tokens_out=response.tokens_out, error=error))                   
    return results
