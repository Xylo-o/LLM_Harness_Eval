# ⚖️ LLM Evaluation Harness

**Choose your LLM judge to evaluate other models using test suites**

**Status:** week 1 of 4 — the end-to-end loop works. Suites are loaded from YAML,
sent to a model, scored, and printed as a table with a meaningful exit code.
Persistence, a second provider, an LLM judge and sandboxed code execution are not
built yet — see [Roadmap](#roadmap).

---

## The problem

Previously, I was evaluating the models by hand, and sometimes it was taking me hours to finish a task and write a solid justification with examples.
Usually, catching obvious mistakes and typos required a lot of time and effort, while a decent model can catch them almost effortlessly in a second.
Then comes the part of writing reports by hand, remembering or jumping between the issue on the screen and making notes about it.
That's why I wanted to make the process more automated.

---

## Demo

[![asciicast](https://asciinema.org/a/XiCWeO22oyOb5bpd.svg)](https://asciinema.org/a/XiCWeO22oyOb5bpd)

---

## Quick start

Requires **Python 3.10+** and an OpenAI API key.

```bash
git clone https://github.com/Xylo-o/LLM_Harness_Eval.git
cd Harness_eval_demo

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
```

Run the built-in suite (feel free to create your own):

```bash
python -m harness --suite suites/basic.yaml
```

Output is a table of every case/scorer pair:

```
                Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Case          ┃ Scorer       ┃ Result ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│ math_simple   │ contains     │ PASS   │
│ math_simple   │ max_words    │ PASS   │
│ capital       │ contains     │ PASS   │
│ ...           │ ...          │ ...    │
└───────────────┴──────────────┴────────┘
```

The process exits **0** if every scorer passed and **1** if any failed, so the
harness can be dropped into CI as-is.

---

## Command line

| Flag | Required | Default | What it does |
|---|---|---|---|
| `--suite` | yes | — | Path to the suite YAML file |
| `--model` | no | `gpt-5.4-mini` | Model name passed to the provider |
| `--no-cache` | no | off | *Parsed but not wired up yet — see [Known limitations](#known-limitations)* |
| `--timeout` | no | — | *Parsed but not wired up yet — see [Known limitations](#known-limitations)* |

---

## How it works

One pass, no concurrency. For each case in the suite: send the prompt, get one
response, run every scorer attached to that case against it.

| Module | Responsibility |
|---|---|
| `harness/cli.py` | Parses arguments, drives the run, sets the exit code |
| `harness/suite.py` | Reads the YAML file into `Suite` / `TestCase` dataclasses |
| `harness/providers.py` | Talks to the model API, returns a `ModelResponse` |
| `harness/cache.py` | Reads and writes responses to `.cache/` on disk |
| `harness/runner.py` | The main loop: case → response → scorers → results |
| `harness/scorers.py` | The scorer functions and the `SCORERS` registry |
| `harness/table.py` | Renders the results table with `rich` |

A scorer is just a function `(response_text, config) -> (passed, detail)`,
registered in the `SCORERS` dict. Adding a new one means writing a function and
adding one line to that dict — there is no plugin system, and deliberately so.

### Caching

Every response is written to `.cache/<sha256>.json`, keyed on the model name plus
the exact prompt text. A second run of an unchanged suite costs nothing and
returns instantly, which matters because the same suite gets run dozens of times
while debugging.

To force fresh calls, delete the cache directory:

```bash
rm -rf .cache/
```

---

## Suite format

A suite is a YAML file with a name and a list of cases. Each case has an `id`, a
`prompt`, and one or more `scorers`. All scorers on a case run against the same
single response.

```yaml
name: basic
cases:
  - id: capital
    prompt: "Answer in one word: the capital of Poland"
    scorers:
      - type: contains
        value: "Warsaw"
      - type: max_words
        value: 1

  - id: crypto
    prompt: "What's the most popular crypto currency?"
    scorers:
      - type: contains_any
        values:
          - "BTC"
          - "Bitcoin"
```

| Field | Meaning |
|---|---|
| `name` | Suite name |
| `cases[].id` | Short identifier, shown in the results table |
| `cases[].prompt` | Sent to the model verbatim |
| `cases[].scorers` | List of scorer configs; `type` picks the scorer, the remaining keys are its arguments |

---

## Scorers

| `type` | Config keys | Passes when |
|---|---|---|
| `contains` | `value` (string) | `value` appears anywhere in the response (case-insensitive) |
| `contains_any` | `values` (list) | at least one entry of `values` appears in the response (case-insensitive) |
| `max_words` | `value` (int) | the response has at most `value` whitespace-separated words |
| `valid_json` | — | the entire response parses as JSON |

`contains` and `contains_any` match substrings, not whole words — `contains: "7"`
also passes on `"17"`. Keep that in mind when writing numeric cases.

---

## Project structure

```
Harness_eval_demo/
├── harness/
│   ├── __init__.py
│   ├── __main__.py       # entry point for `python -m harness`
│   ├── cli.py            # argument parsing, exit code
│   ├── providers.py      # model API client + ModelResponse
│   ├── cache.py          # on-disk response cache
│   ├── suite.py          # YAML loading
│   ├── runner.py         # main loop
│   ├── scorers.py        # scorer functions + registry
│   └── table.py          # rich output
├── suites/
│   └── basic.yaml        # 6 example cases
├── tests/
├── requirements.txt
└── .gitignore
```

---

## Known limitations

Deliberate scope cuts and known defects, kept honest rather than hidden.

**Deliberate, for now:**

- **Single-threaded.** Cases run one after another. At six cases the wall-clock
  cost of concurrency is not worth the debugging cost of async stack traces.
- **One provider.** Only an OpenAI-compatible client is implemented. A second
  provider behind the same `complete(prompt) -> ModelResponse` interface is
  planned for week 2.
- **No persistence.** Results are printed and discarded. Comparing two runs, which
  is the point of the whole project, needs a database — week 2.
- **Substring scorers only.** No semantic or open-ended grading yet; every check is
  exact-match or structural. An LLM judge is week 2.

**Defects that need fixing:**

- `pytest` does not run at all.
- `--no-cache` and `--timeout` are declared in the CLI but ignored by the runner.
- There is no `.env.example`

---

## Roadmap

- **Week 2** — SQLAlchemy models and run persistence; a second provider; an LLM
  judge that stores its reasoning, not just its verdict; `harness compare A B` to
  surface PASS→FAIL and FAIL→PASS between two runs.
- **Week 3** — generated-code cases executed against real pytest suites in a
  subprocess; a failure taxonomy derived from ~20 actual observed failures rather
  than guessed up front.
- **Week 4** — FastAPI wrapper, Docker Compose with Postgres, GitHub Actions.

---

## License

**MIT License**
