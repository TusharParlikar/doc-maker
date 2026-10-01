# ADR template

One record per significant decision. Put them in `docs/DECISIONS.md` (several ADRs) or `docs/adr/NNNN-title.md` (one per file) if the project already uses that layout. Every statement needs evidence: code, config, commit history, or an issue. Mark reconstructed reasoning as an assumption.

```markdown
## ADR-<NNNN>: <Decision as a short statement, e.g. "Use PostgreSQL for transactional data">

- **Status:** Accepted | Superseded by ADR-<NNNN> | Proposed
- **Date:** <from git history if known, else "unknown">
- **Evidence:** `<path/to/file>:<line>`, commit `<sha>` <!-- what shows this decision was made -->

### Context
<The situation and constraints at the time. 2-4 sentences.>

### Problem
<The question that needed an answer.>

### Options considered
| Option | Pros | Cons |
|--------|------|------|
| <A (chosen)> | | |
| <B> | | |

### Decision
<What was chosen.>

### Rationale
<Why, tied to the constraints. Say "assumption" where the reason is inferred, not recorded.>

### Consequences
- **Positive:** <...>
- **Negative / trade-offs:** <...>
- **Follow-ups:** <what this decision requires or rules out later>
```
