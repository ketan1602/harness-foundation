# harness-foundation

A small, framework-neutral agent harness. Every tool call goes through one mediator that
authorizes it against a manifest, enforces budgets, and records telemetry.

```
src/agent_platform/   manifest, registry, policy, budget, tools, telemetry, harness
manifests/            declarative agent manifests (YAML)
examples/             run_demo.py and exp1..exp3 (direct vs harnessed, blocked tool, budget)
tests/                pytest suite
```

## Run

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'
pytest
python examples/run_demo.py
```
