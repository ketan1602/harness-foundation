# harness-foundation

A small, framework-neutral agent harness. Every tool call goes through one mediator that
authorizes it against a manifest, enforces budgets, and records telemetry.

```
src/agent_platform/   manifest, registry, policy, budget, tools, telemetry, harness
manifests/            declarative agent manifests (YAML)
examples/             run_demo.py, registry_demo.py, exp1..exp3 (direct vs harnessed, blocked tool, budget)
tests/                pytest suite
```

## Run

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'
pytest
python examples/run_demo.py
```

## Run with an LLM

Install the SDK that provides your async chat client, then configure it in `.env` (gitignored):

```bash
pip install -e '.[llm]'
cp .env.example .env   # set LLM_CLIENT (module:Class), LLM_API_KEY, LLM_MODEL
python examples/run_llm_demo.py "The checkout page is down"
```
