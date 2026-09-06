from dataclasses import dataclass, field
from .providers import OpenAIProvider
from .scorers import SCORERS

@dataclass
class ScoreResult:
    scorer_name: str
    passed: bool
    detail: dict

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


def runner(suite, model: str):
    provider = OpenAIProvider(model=model)
    results = []
    for case in suite.cases:
        try:
            response = provider.complete(case.prompt)
        except Exception as e:
            results.append(CaseResult(case_key=case.id, prompt=case.prompt, scorer_config=case.scorers, error=str(e),))
            continue
        scores = []
        for cfg in case.scorers:
            passed, detail = SCORERS[cfg["type"]](response.text, cfg)
            scores.append(ScoreResult(scorer_name=cfg["type"], passed=passed, detail=detail))
        results.append(
            CaseResult(
                case_key=case.id,
                prompt=case.prompt,
                scorer_config=case.scorers,
                response=response.text,
                latency_ms=response.latency_ms,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                scores=scores,
            )
        )                   
    return results
