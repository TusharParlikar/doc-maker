# Evals

Behaviour tests for the three skills, run with [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals). Each case runs with the plugin and without it (the no-plugin baseline) and reports the difference as `Δ`.

> [!WARNING]
> Every run is a real model call billed to your account. A full run is about 7 cases × 3 runs × 2 arms = 42 agent runs, plus judge calls. Start with the smoke cases and `--runs 1`.

## Cases

| Case | Tag | Skill | What it proves |
|------|-----|-------|----------------|
| `trap-stale-docs` | smoke | doc-maker | Finds 4 planted errors in a README (wrong commands, port, env var, endpoint) and fixes them |
| `trap-invented-features` | smoke | doc-maker | Writes a README without inventing endpoints, auth, a database or tests |
| `trap-secret` | smoke | doc-maker | Documents configuration without leaking a hard-coded key or `.env` values, and flags them |
| `no-trigger-question` | smoke | none | A question about code gets an answer, not a documentation run |
| `readme-realworld` | full | doc-maker | README for [node-express-realworld-example-app](https://github.com/gothinkster/node-express-realworld-example-app) @ `30b68e1` |
| `database-microblog` | full | database-docs | ER diagram + data dictionary for [microblog](https://github.com/miguelgrinberg/microblog) @ `a975ef6` |
| `infra-fastapi-template` | full | architecture-docs | Deployment and CI/CD docs for [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) @ `cb740b6` |

Real repositories are pinned by commit, so the ground truth in each `accurate.md` grader stays valid.

## Run

From the repository root (the plugin root):

```bash
# cheap first pass: synthetic traps, one run each
claude plugin eval . --tag smoke --runs 1 --scaffold --allow-tools Write Edit Bash --judge-model sonnet

# full suite
claude plugin eval . --scaffold --allow-tools Write Edit Bash --judge-model sonnet --max-cost-usd 40
```

- `--scaffold` runs each case's `fixture.sh` (it creates the synthetic repo or clones the pinned one). Review the scripts before you pass it.
- `--allow-tools Write Edit Bash` lets the agent write the docs and run `evidence.py`. Bash runs inside Claude Code's sandbox.
- `--judge-model sonnet` is recommended: the `accurate.md` rubrics judge long documents.

Results go to `evals/results/` (git-ignored). Open the HTML report path that the command prints.

## Free checks (no model calls)

```bash
python3 tests/test_evidence.py   # evidence.py on synthetic repos, including the trap fixtures above
python3 tests/test_skills.py     # rule IDs, cross-references, templates, frontmatter
claude plugin validate --strict .
```
