# connexity-evals

CLI tool for running and managing [Connexity](https://github.com/Connexity-AI/connexity-evals) agent evaluations in CI/CD pipelines and local developer workflows.

`connexity-evals` is a lightweight command-line client that communicates with a Connexity Evals API server. It lets you trigger eval runs, inspect results, and manage scenarios — all from the terminal or your CI pipeline.

## Installation

```bash
pip install connexity-evals
```

## Authentication

The CLI authenticates against a Connexity Evals API server using a Bearer token.

Set the following environment variables:

| Variable | Description | Default |
|---|---|---|
| `CONNEXITY_EVALS_API_URL` | Base URL of the Connexity Evals API | `http://localhost:8000` |
| `CONNEXITY_EVALS_API_TOKEN` | Bearer JWT for authentication | *(required)* |

Or pass them as flags:

```bash
connexity-evals --api-url https://evals.example.com --token "$TOKEN" run ...
```

## Usage

### Run an evaluation

```bash
# Trigger a run against a scenario set and wait for completion
connexity-evals run --scenarios checkout-tests --agent my-staging-agent

# Stream SSE progress events in real time
connexity-evals run --scenarios smoke-test --agent my-agent --stream

# JSON output for CI/CD parsing
connexity-evals run --scenarios regression --agent my-agent --output json
```

### Inspect results

```bash
# List recent runs
connexity-evals results list

# Show detailed results for a specific run
connexity-evals results show <run-id>
```

### Manage scenarios

```bash
# List scenarios with filters
connexity-evals scenarios list --tag red-team

# Import scenarios from a JSON file
connexity-evals scenarios import scenarios.json

# Export scenarios to a file
connexity-evals scenarios export --file exported.json

# Generate scenarios using an LLM
connexity-evals scenarios generate --prompt agent-prompt.txt --tools tools.json --count 20
```

### Output formats

All commands support `--output json` (machine-readable) and `--output table` (human-readable, default).

```bash
# Global default
connexity-evals --output json results list

# Per-command override
connexity-evals results list --output json
```

## CI/CD Integration

### GitHub Actions

```yaml
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install connexity-evals

      - name: Run evaluations
        env:
          CONNEXITY_EVALS_API_URL: ${{ secrets.EVALS_API_URL }}
          CONNEXITY_EVALS_API_TOKEN: ${{ secrets.EVALS_API_TOKEN }}
        run: |
          connexity-evals run \
            --scenarios regression-suite \
            --agent staging-agent \
            --output json
```

### GitLab CI

```yaml
eval:
  image: python:3.12-slim
  script:
    - pip install connexity-evals
    - connexity-evals run
        --scenarios regression-suite
        --agent staging-agent
        --output json
  variables:
    CONNEXITY_EVALS_API_URL: $EVALS_API_URL
    CONNEXITY_EVALS_API_TOKEN: $EVALS_API_TOKEN
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Run completed successfully |
| `1` | Run failed, was cancelled, or an API error occurred |
| `2` | Timeout waiting for run completion |

## Links

- [Repository](https://github.com/Connexity-AI/connexity-evals)
- [Issue Tracker](https://github.com/Connexity-AI/connexity-evals/issues)

## License

MIT
