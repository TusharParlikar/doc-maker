# Operations templates: API ↔ database map, runbook, technical debt register

## API ↔ database map

Start from `evidence.py routes` and `evidence.py schema`, then open each handler to confirm what it reads and writes.

```markdown
| Endpoint | Method | Reads | Writes | Transaction | Notes |
|----------|--------|-------|--------|-------------|-------|
| `/orders` | POST | `users`, `products` | `orders`, `order_items`, `products.stock` | ✅ `services/order.ts:40-71` | Row locks with `FOR UPDATE` |
| `/orders/:id/cancel` | POST | `orders` | `orders.status`, `products.stock` | ❌ | ⚠️ two writes without a transaction |
```

Optional diagram: endpoints on the left, tables on the right, writes and reads in different colours. Keep it under ~15 edges; past that, the table is clearer.

## Runbook

```markdown
### Runbook: <incident, e.g. "Database unavailable">

- **Detect:** <alert name / symptom / dashboard> <!-- only alerts that exist; else say "no alert configured" -->
- **Impact:** <what users see>
- **Owner:** <team or role, if documented>

1. <Check step, with the exact command or console path.>
2. <Mitigation step.>
3. <Recovery step, e.g. restore from the latest backup: command, expected time.>
4. <Verify recovery: health check URL / query.>

**Rollback / escalation:** <...>
**Last tested:** <date, or "never tested": say so>
```

## Technical debt register

```markdown
| ID | Item | Location | Impact | Risk | Effort | Suggested fix |
|----|------|----------|--------|------|--------|---------------|
| D1 | Cancel flow writes without a transaction | `services/order.ts:120` | Stock can drift | High | S | Wrap both writes in one transaction |
| D2 | 37 TODO/FIXME comments | `grep -rn "TODO\|FIXME"` | Unknown work | Low | M | Triage into issues |
```

Impact and Risk: High / Medium / Low. Effort: S (< 1 day), M (< 1 week), L (more). Sort by Impact × Risk; list quick wins (high impact, S effort) first. Describe the code, never the people.
