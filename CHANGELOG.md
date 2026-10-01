# Changelog

## 2.0.0

Breaking: rules are renumbered and merged. If you referenced rule numbers (in prompts, forks or team docs), use the mapping below.

### Added
- **Evidence script** `scripts/evidence.py` in every skill (Python standard library, read-only): `inventory`, `env`, `deps`, `routes`, `schema`, `docs`. Reports `file:line` locations; never prints secret values.
- **Self-check** of written docs: broken links and anchors, commands that don't exist, endpoints not in the code, env vars the code never reads.
- **Templates** in `references/`: README, ADR, data dictionary and ER conventions, role-permission matrix, STRIDE threat model, API ↔ database map, runbook, technical debt register.
- **Tiers** on every rule (1 always, 2 when present, 3 on request) and **length budgets** (README ~1,200-2,000 words, each `docs/*.md` ≤ 2,500).
- **Feedback loop**: evidence score per section (high / medium / low), revise only the sections the user names, optional `.doc-maker.md` preferences file written only with approval.
- **Eval suite** in `evals/` for `claude plugin eval`: 3 real repositories pinned by commit, 3 trap repositories, 1 must-not-trigger case, each scored against a no-plugin baseline.
- **Free checks**: `tests/test_evidence.py`, `tests/test_skills.py`, and a GitHub Actions workflow running them.
- `docs/COMPARISON.md`: the full comparison, with rows where alternatives win.

### Changed
- 85 rules → 51: `doc-maker` D1-D20, `database-docs` DB1-DB12, `architecture-docs` A1-A19. Every rule is *Look for → Verify → Output*.
- `doc-maker` description no longer triggers on plain questions about code.
- README cut from ~4,200 to ~1,200 words; rule index, recipes and troubleshooting live in `GUIDE.md`.

### Rule mapping (1.x → 2.0)

"Process" and "Standards" mean the rule became part of the skill's Process steps or Writing standards instead of a separate rule.

| 1.x | 2.0 | 1.x | 2.0 | 1.x | 2.0 |
|----:|-----|----:|-----|----:|-----|
| 1 | Standards | 30 | Process + readme-template | 59 | DB1 |
| 2 | D1 | 31 | Standards + Process | 60 | Process (database-docs) |
| 3 | D1 | 32 | Process | 61 | A1 |
| 4 | D2 | 33 | Process + Standards | 62 | A1 |
| 5 | DB3 | 34 | Process + D20 | 63 | DB10 |
| 6 | D6, A3 | 35 | Standards | 64 | A5 |
| 7 | D7 | 36 | D16 | 65 | A4 |
| 8 | D8 | 37 | D13 | 66 | A3 |
| 9 | D16 | 38 | D19 | 67 | A6 |
| 10 | D3 | 39 | D19, A19 | 68 | A7 |
| 11 | D2 | 40 | D20 | 69 | A8 |
| 12 | D9 | 41 | DB1 | 70 | A6 |
| 13 | D10 | 42 | DB2 | 71 | A3 |
| 14 | D6 | 43 | DB3 | 72 | A9 |
| 15 | D12, A1, A2 | 44 | DB3 | 73 | A9 |
| 16 | D12, A6 | 45 | DB5 | 74 | A10 |
| 17 | D4 | 46 | DB4 | 75 | A11 |
| 18 | D5 | 47 | DB5 | 76 | A12 |
| 19 | A15 | 48 | DB6 | 77 | A13 |
| 20 | A13 | 49 | DB7 | 78 | A14 |
| 21 | D11 | 50 | DB8 | 79 | A15 |
| 22 | D12, A12 | 51 | DB9 | 80 | A16 |
| 23 | D13 | 52 | DB12 | 81 | A17 |
| 24 | A2 | 53 | DB5 | 82 | A2 |
| 25 | D14 | 54 | DB11 | 83 | A15 |
| 26 | D15 | 55 | DB10 | 84 | A18 |
| 27 | D18 | 56 | DB1 | 85 | A19 |
| 28 | A4, D18 | 57 | DB2 | | |
| 29 | D17 | 58 | DB1 | | |

## 1.1.1
- `doc-maker`: added the "update existing docs" step (list mismatches, then fix), a hand-over step, and the read-only rule.
- Docs aligned with the skills; corrected the Claude.ai upload path.

## 1.1.0
- Added `architecture-docs` (rules 61-85).

## 1.0.0
- First release: `doc-maker` (rules 1-40) and `database-docs` (rules 41-60), packaged as a Claude Code plugin and Agent Skills.
