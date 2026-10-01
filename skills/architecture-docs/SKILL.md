---
name: architecture-docs
description: Document a system's architecture, security and operations in depth, evidence-first - auth model and role-permission matrix, STRIDE threat model, components and dependency graph, sequence diagrams, entity lifecycles, deployment and environments, cloud infrastructure, CI/CD, external services and third-party APIs, caching, queues and events, logging and monitoring, error handling, disaster recovery, scalability and bottlenecks, cost, technical debt, future architecture, docs change checklist. Use when asked for any of these, or when doc-maker needs architecture, security or operations depth.
---

# architecture-docs

Document how the system is built, secured, deployed, operated and evolved, so another engineer can run it, change it
safely and plan its future. Companions: **doc-maker** (D1-D20) and **database-docs** (DB1-DB12). Rule IDs here are
A1-A19.

## Process

1. **Collect evidence with the script.** Run `python3 <this skill's directory>/scripts/evidence.py inventory <repo>`
   (CI, containers, Kubernetes, IaC, platform files), then `routes`, `deps` and `env` as relevant. Read the files it
   lists: Dockerfiles, compose, manifests, Terraform/CloudFormation/Pulumi/CDK/Bicep, CI configs, auth middleware,
   cache and queue clients, logging setup, error handlers. Use `python` if `python3` isn't found. If Python isn't available, read them directly.
2. **Stay read-only.** Only commands that change nothing (dependency trees, `--help`, tests, `EXPLAIN`). Never
   `terraform apply`, deploy, migrate, call cloud APIs that modify resources, or send real messages, emails or
   payments. Never print secrets; refer to them by name or file:line.
3. **Select rules.** If the user asked for one topic, write that rule only. For a full architecture document:
   Tier 1 always, Tier 2 when the evidence exists (one line "not present" when its absence matters, e.g. "No CI: tests
   are not run before deploy"), Tier 3 only on request.
4. **Write each topic once.** These rules hold the depth; doc-maker D12 keeps only a summary and links here. Database
   detail lives in database-docs (DB10 holds the API ↔ database mapping, DB12 database backups).
5. **Separate implemented from recommended.** Label every recommendation, estimate and proposed component. Never claim
   failover, autoscaling, alerting or backups that configuration doesn't show.
6. **Write** with the templates in `references/`: `security-templates.md` (A1 role matrix, A2 STRIDE) and
   `operations-templates.md` (runbooks for A14, debt register for A17, API ↔ database table). Default files, each
   ≤ 2,500 words; small projects keep everything in `docs/ARCHITECTURE.md`:

   | File | Rules |
   |------|-------|
   | `docs/ARCHITECTURE.md` | A3, A4, A5, A9, A10, A11, A13, A18 |
   | `docs/SECURITY.md` | A1, A2 |
   | `docs/INFRASTRUCTURE.md` | A6, A7, A8, A14, A15, A16 |
   | `docs/OPERATIONS.md` | A12 (and runbooks from A14) |
   | `docs/TECH_DEBT.md` | A17 |
   | `docs/MAINTAINING_DOCS.md` | A19 |

7. **Diagrams:** `flowchart` with subgraphs for structure, `sequenceDiagram` for flows, `stateDiagram-v2` for
   lifecycles. Same component names in every diagram and document; ~15 nodes or edges at most per diagram.
8. **Hand over** with an evidence score per section (*high* / *medium* / *low*), findings (⚠️ gaps), assumptions and
   open questions; ask which sections to improve and revise only those.

## Rules

Each rule: **Look for** · **Verify** · **Output**.

**A1. Authentication, authorization and role-permission matrix** · Tier 2
- Look for: auth libraries in `evidence.py deps`, middleware/guards/decorators, session or JWT config, OAuth/OIDC/SSO
  setup, API keys, policy files, role enums, seed data with roles, row-level security.
- Verify: for every route from `evidence.py routes`, find the check that protects it. Unprotected routes, checks done
  only in the frontend, and hard-coded credentials (file:line, never the value) are findings.
- Output: methods and where they're enforced; token/session lifecycle (issue, storage, expiry, refresh, revocation,
  logout); authorization model (RBAC, ABAC, ownership, tenant isolation); sequence diagram for login and for a denied
  request; role-permission matrix from the template with the enforcement location per cell.

**A2. Security threat model and privacy** · Tier 3
- Look for: assets, actors, entry points (routes, webhooks, queues, uploads), trust boundaries from A3/A6, personal data
  (database-docs DB9), third parties receiving data (A9), input validation, rate limiting, secrets management.
- Verify: each mitigation listed has file:line evidence; otherwise it's a gap.
- Output: data-flow diagram with trust boundaries; STRIDE table (threat, likelihood, impact, mitigation, gap);
  privacy notes (data retention, logging of personal data, third-party sharing). Mention compliance regimes only when
  the data or market clearly brings them in, and say they need legal review. Never include exploit steps.

**A3. Components and dependency graph** · Tier 1
- Look for: services, packages and modules (imports, directory layout), internal dependencies, layering rules;
  external dependencies from `evidence.py deps`; generated graphs where a tool is installed (`madge`, `pydeps`,
  `go mod graph`, `cargo tree`, `mvn dependency:tree`).
- Verify: structure comes from imports and config, not from intended design; cycles and layer violations are findings.
- Output: component diagram (subgraph per service or layer) with one-line responsibilities; critical, heavy,
  unmaintained or duplicated dependencies; pinning and update tooling (Dependabot, Renovate); known vulnerabilities
  only if a read-only audit ran (`npm audit`, `pip-audit`, `cargo audit`).

**A4. Key flows** · Tier 1
- Look for: the main user journey, auth, the most important write (payment, order, publish), background jobs, key
  integrations.
- Verify: follow each flow through the code in execution order, including async hops.
- Output: 3-5 `sequenceDiagram`s with actors, services, databases, caches, queues and external systems; at least one
  failure path (timeout, validation error, outage) per critical flow, with retries shown.

**A5. Entity lifecycles** · Tier 2 (entities with a status or workflow)
- Look for: status enums and columns, state-changing code, jobs and webhooks that change state.
- Verify: every transition exists in code; transitions the code allows but the design doesn't intend, and states
  with no exit, are findings.
- Output: `stateDiagram-v2` per entity; each transition names its trigger (endpoint, job, webhook, timeout) and guard.

**A6. Deployment and environments** · Tier 1
- Look for: `evidence.py inventory` (`containers`, `kubernetes`, `platform`, `iac`), Procfiles, compose files,
  environment-specific config, preview deployments.
- Verify: each runtime component and environment is defined in config, not just mentioned.
- Output: deployment diagram (what runs where: processes, containers, functions, workers, cron, regions; ports,
  ingress, TLS, replicas, resource limits, health checks); table of environments (local, dev, preview, staging,
  production) with how each is created, data source, config differences, external services in sandbox or live mode,
  and access; promotion path; drift that makes staging unreliable.

**A7. Cloud infrastructure** · Tier 2
- Look for: IaC resources (compute, storage, databases, VPCs/subnets/security groups, IAM, DNS, CDN, secret stores).
- Verify: resources come from IaC or provider config; without IaC, state "managed by hand; not verifiable from the
  repository".
- Output: resource diagram separating public and private networks; IAM roles and scope; findings for wildcard
  permissions, public buckets and open security groups.

**A8. CI/CD pipeline** · Tier 2
- Look for: `evidence.py inventory` (`ci`): GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure Pipelines, Bitbucket.
- Verify: triggers, jobs, order, conditions and gates come from the config files.
- Output: flowchart from commit to production (build, lint, test, scan, artifact, migrations, deploy, approvals,
  smoke tests); secrets used (names only); caches; target environments; rollback procedure; missing gates as findings.

**A9. External services and third-party APIs** · Tier 2
- Look for: SDK clients in `evidence.py deps`, outbound HTTP calls, webhook handlers, config keys in `evidence.py env`.
- Verify: each integration is called from code; webhook signature checks and idempotency exist where claimed.
- Output: per integration: purpose, data sent and received, auth, config keys (names), client, timeouts and retries,
  rate limits and quotas, API version, behaviour when it's slow or down, link to the provider's docs. Mark data that
  leaves the system. Findings: deprecated versions, missing signature checks, unhandled error codes.

**A10. Caching** · Tier 2 (state "no caching" when none exists)
- Look for: HTTP cache headers, CDN config, in-memory caches, Redis/Memcached clients, memoization, materialized data.
- Verify: key format, TTL and invalidation come from code.
- Output: per cache layer: what, key, TTL, invalidation trigger, size and eviction; when users can see stale data;
  stampede and cold-start handling. New caching only as a labelled recommendation with evidence.

**A11. Queues and events** · Tier 2
- Look for: Kafka, RabbitMQ, SQS/SNS, Pub/Sub, Redis Streams, Celery, Sidekiq, BullMQ, cron and scheduled jobs.
- Verify: producers and consumers are found in code for each message type.
- Output: event-flow diagram; per message: producer, consumers, payload schema, ordering, delivery semantics,
  retries, dead-letter handling, idempotency, schema versioning.

**A12. Logging and monitoring** · Tier 2
- Look for: logging libraries and config, OpenTelemetry, metrics, tracing, Sentry/Datadog/CloudWatch/Grafana/
  Prometheus config, health-check endpoints, alert definitions.
- Verify: list only dashboards and alerts that exist in config; the rest are recommendations.
- Output: telemetry pipeline diagram; log format, levels, correlation IDs, retention, redaction of personal data and
  secrets; what to monitor in production (key metrics and failure signals).

**A13. Error handling and reliability** · Tier 2
- Look for: error types, global handlers, error middleware, retry/timeout/circuit-breaker libraries, fallbacks.
- Verify: trace a failing request end to end; swallowed exceptions, broad catch-alls and stack traces sent to
  clients are findings.
- Output: error model; API error format and status-code mapping; what users see vs what is logged; retries,
  timeouts, circuit breakers, fallbacks and graceful degradation; important failure scenarios and expected behaviour.

**A14. Disaster recovery** · Tier 2 (state "no RTO/RPO defined" when none exists)
- Look for: RTO/RPO statements, multi-zone or multi-region config, replication, failover, database backups
  (database-docs DB12), infrastructure recreation from IaC.
- Verify: separate configured mechanisms from intentions; whether restores or failovers have been tested.
- Output: recovery runbooks (template) for database loss, region or provider outage, credential compromise,
  accidental deletion and bad deploy. Never claim recovery capability the configuration doesn't show.

**A15. Scalability and performance bottlenecks** · Tier 3
- Look for: scaling config (autoscaling, replicas, workers, pool sizes), stateful components, load-test results,
  profiles, query plans, N+1 queries, synchronous external calls, large payloads, missing pagination.
- Verify: label every capacity or latency figure as measured (with source) or estimated; when unmeasured, say how to
  measure it.
- Output: scaling dimensions and current limits; what breaks first at 10x and 100x; bottlenecks with location, cause,
  impact and fix options, ordered by user impact.

**A16. Cost** · Tier 3
- Look for: compute, storage, data transfer, managed services, third-party and LLM API usage, licences (from IaC,
  platform config, `evidence.py deps`).
- Verify: prices from official pricing pages with the date checked; never invented totals: when usage is unknown,
  give the formula.
- Output: cost drivers mapped to components and billing units; cost controls in place (budgets, quotas, caching,
  batching); savings as labelled recommendations.

**A17. Technical debt** · Tier 3
- Look for: TODO/FIXME/HACK comments, deprecated or outdated dependencies, dead code, duplicated logic, missing tests,
  disabled lint rules, workarounds, findings from the other rules.
- Verify: each item is still present in the code.
- Output: debt register (template): location, impact, risk, effort (S/M/L), suggested fix; quick wins first. Describe
  the code, never the people.

**A18. Future architecture** · Tier 3
- Look for: roadmap (doc-maker D15), A15 limits, A17 debt, A2 gaps.
- Verify: each proposed change is justified by a current, evidenced limitation.
- Output: target-architecture diagram labelled "proposed"; incremental migration steps with dependencies and risks;
  ADRs for significant choices (doc-maker D13). No speculative rewrites.

**A19. Documentation change checklist** · Tier 3
- Look for: which code areas each document depends on.
- Output: map of code paths to docs (e.g. `src/auth/**` → `docs/SECURITY.md` role matrix); pull-request checklist
  (new endpoint, env var, table or migration, dependency, integration, role, infrastructure change); automation
  suggestions (CODEOWNERS for docs, PR template checkbox, CI running `evidence.py docs`, `tbls diff`). Edit
  `CONTRIBUTING.md` or the PR template only when the user asks.
