---
name: architecture-docs
description: Document a project's architecture and operations in depth, evidence-first - authentication/authorization model, role-permission matrix, API-to-database mapping, entity lifecycle (state) diagrams, sequence and component diagrams, deployment and cloud infrastructure, CI/CD pipelines, environments, dependency graph, external services and third-party APIs, caching, message queues/events, logging and monitoring, error handling, disaster recovery, scalability, cost, technical debt, security threat model (STRIDE), performance bottlenecks, future architecture and a documentation change checklist. Use when asked for any of these, when documenting a system with deployment/infra/CI, auth, integrations, queues or caches, or when doc-maker needs architecture or operations depth.
---

# architecture-docs

## Purpose
Document how a system is built, secured, deployed, operated and evolved, in enough depth that another engineer can run it, change it safely and plan its future.
Companion to the **doc-maker** skill (rules 1-40) and the **database-docs** skill (rules 41-60); rules numbered 61-85 continue that numbering.

## How to apply (read first)

1. **Find the evidence.** Auth middleware and policy files, route definitions, Dockerfiles and compose files, Kubernetes manifests, IaC (Terraform, CloudFormation, Pulumi, CDK, Bicep), platform configs (Vercel, Netlify, Render, Fly, Heroku), CI configs, lockfiles, cache and queue clients, logging/telemetry setup, error handlers, environment files (`.env.example`, never real `.env` values), and git history.
2. **Stay read-only.** Run only commands that don't change anything: dependency-tree tools, linters, `--help`, test suites, `EXPLAIN`. Never run `terraform apply`, deploys, migrations, cloud CLI commands that modify resources, or anything that sends real messages, emails or payments. Never print secrets; refer to them by name or by file and line.
3. **Relevance.** Apply a rule only when the project has the thing it covers. When something is absent, say so in one line and state the consequence (e.g. "No CI pipeline: tests are not run before deploy").
4. **Don't duplicate.** Several rules deepen earlier ones (65 deepens 28, 67 deepens 16, 76 deepens 22, 77 deepens 20, 79 deepens 19, 82 deepens 15 and 24, 84 deepens 26, 63 is the endpoint view of 55). Write each topic once and link to it from the other places.
5. **Separate implemented from recommended.** Label every recommendation, estimate and proposed component as such. Never claim a capability (failover, autoscaling, alerting) that the code or configuration doesn't show.
6. **Diagrams.** Use Mermaid: `sequenceDiagram` (65), `flowchart` with subgraphs (66, 67, 68, 69, 71), `stateDiagram-v2` (64). Use the same component names in every diagram and document (rule 32).
7. **Output.** Create only the files the project needs; small projects can keep everything in `docs/ARCHITECTURE.md`. Typical split:

   | File | Rules |
   |------|-------|
   | `docs/ARCHITECTURE.md` | 63-66, 71, 74, 75, 77, 84 |
   | `docs/SECURITY.md` | 61, 62, 82 |
   | `docs/INFRASTRUCTURE.md` | 67-70, 78-80 |
   | `docs/INTEGRATIONS.md` | 72, 73 |
   | `docs/OPERATIONS.md` | 76 (and runbooks from 78) |
   | `docs/TECH_DEBT.md` | 81, 83 |
   | `docs/MAINTAINING_DOCS.md` | 85 |

## Rules

61. Authentication & Authorization Model
   - Document every authentication method actually implemented (sessions, JWT, OAuth/OIDC, SSO, API keys, mTLS) and where it is enforced (middleware, gateway, service, database).
   - Explain the token/session lifecycle: issue, storage, expiry, refresh, revocation and logout.
   - Document the authorization model (RBAC, ABAC, ownership checks, tenant isolation, row-level security) and the code location of each check.
   - Include a sequence diagram for login and for an authorized request, including the rejection path.
   - Flag unprotected endpoints, checks done only in the frontend, and hard-coded credentials (by file and line, never the value).

62. Role-Permission Matrix
   - Derive roles and permissions from code, policy files, configuration or seed data, not from assumptions.
   - Present a matrix with roles as columns and resource/action pairs as rows; mark each cell allowed, denied or conditional.
   - State the conditions (own records only, same tenant, feature flag, plan tier).
   - Cite where each permission is enforced; flag permissions that are defined but never checked, and checks that reference undefined roles.

63. API ↔ Database Mapping
   - For each important endpoint, list the tables/collections it reads and writes, the operation type, and the transaction boundary.
   - Present as a table: endpoint | method | reads | writes | transaction | notes.
   - Identify N+1 query patterns, multi-table writes without a transaction, and tables written by many endpoints.
   - Keep it consistent with database-docs rule 55, which gives the entity-centric view of the same mapping.

64. Entity Lifecycle Diagrams
   - For entities with a status or workflow (order, payment, job, subscription, user account), draw a Mermaid `stateDiagram-v2`.
   - Derive states and transitions from enums, status columns and the code that changes them.
   - Show what triggers each transition (user action, job, webhook, timeout) and its guards; mark initial and terminal states.
   - Flag transitions the code allows but the design doesn't intend, and states with no way out.

65. Sequence Diagrams
   - Choose the 3-5 most important flows: the main user journey, authentication, payment or other critical writes, background jobs, and key integrations.
   - Show actors, services, databases, caches, queues and external systems in the order the code executes them, including asynchronous hops.
   - Include at least one failure path per critical flow (timeout, validation error, external outage) and show retries.
   - Name participants exactly as in the architecture and component diagrams.

66. Component Diagrams
   - Show the internal modules or packages of each service, the interfaces between them, and their dependencies.
   - Derive the structure from imports and directory layout, not from intended design alone.
   - Document layering rules (for example controllers → services → repositories) and list violations found.
   - Give each component a one-line responsibility.

67. Deployment Architecture
   - Show what runs where: processes, containers, serverless functions, workers, scheduled jobs, hosts and regions, and how they connect.
   - Derive it from Dockerfiles, compose files, Kubernetes manifests, IaC, Procfiles and platform configuration.
   - Document ports, protocols, ingress and load balancing, TLS termination, replicas, resource limits and health checks.
   - Mark components that are planned or documented elsewhere but not actually deployed.

68. Cloud Infrastructure Architecture
   - Inventory cloud resources from IaC or provider configuration: compute, storage, databases, networking (VPCs, subnets, security groups, firewalls), IAM, DNS, CDN, secrets stores.
   - Diagram resource relationships and network boundaries, separating public from private.
   - Document IAM roles and their scope; flag wildcard permissions, public buckets and open security groups.
   - If there is no IaC, state that the infrastructure is managed by hand and cannot be verified from the repository.

69. CI/CD Pipeline Documentation
   - Document every pipeline from its configuration (GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure Pipelines, Bitbucket): triggers, jobs, order, conditions and gates.
   - Draw the path from commit to production: build, lint, test, security scan, artifact, migrations, deploy, approvals, smoke tests.
   - Document secrets used (by name only), caches, target environments and the rollback procedure.
   - Flag missing gates, such as no tests on pull requests, no approval before production, or migrations without a backup step.

70. Environment Architecture
   - List every environment (local, development, test, preview, staging, production) and how each is created.
   - Tabulate differences: infrastructure, data source, configuration, feature flags, external services in sandbox or live mode, and who has access.
   - Document the promotion path between environments and the configuration and secrets each one needs (names only).
   - Flag drift between staging and production that would make testing unreliable.

71. Dependency Graph
   - Internal: graph how modules or services depend on each other and highlight cycles.
   - External: list direct dependencies from manifests and lockfiles with their purpose; highlight critical, heavy, unmaintained or duplicated packages.
   - Document the version-pinning strategy, update tooling (Dependabot, Renovate) and known vulnerabilities if a read-only audit is available (`npm audit`, `pip-audit`, `cargo audit`).
   - Prefer generated graphs (`madge`, `pydeps`, `go mod graph`, `cargo tree`, `mvn dependency:tree`) over reading imports by hand.

72. External Services & Integrations
   - Inventory every external system the project talks to: SaaS APIs, payments, email/SMS, identity providers, LLM APIs, object storage, analytics, and webhooks in both directions.
   - For each: purpose, data sent and received, authentication method, configuration keys (names only), client library, and timeout/retry behaviour.
   - Diagram the integration boundaries and mark which data leaves the system (see rule 24).
   - Document what happens when each service is slow or down.

73. Third-Party API Documentation
   - For each third-party API: endpoints used, fields the code relies on, API version, rate limits, quotas, pricing unit, timeouts and retries.
   - Link the provider's official documentation instead of copying it.
   - For incoming webhooks: signature verification, idempotency, retry behaviour and ordering assumptions.
   - Flag deprecated API versions, missing signature checks and unhandled error codes.

74. Caching Architecture
   - Document each cache layer: HTTP/browser, CDN, in-process memory, distributed cache (Redis, Memcached), query cache, and precomputed or materialized data.
   - For each: what is cached, key format, TTL, invalidation trigger, size limit and eviction policy.
   - Explain consistency trade-offs, when users can see stale data, and how stampedes and cold starts are handled.
   - If there is no caching, say so; propose caching only as a labelled recommendation backed by evidence.

75. Message Queue / Event Architecture
   - Inventory brokers, queues, topics, streams and job systems (Kafka, RabbitMQ, SQS/SNS, Pub/Sub, Redis Streams, Celery, Sidekiq, BullMQ, cron).
   - For each message or event: producer, consumers, payload schema, ordering guarantee, delivery semantics (at-most-once, at-least-once, effectively-once), retries and dead-letter handling.
   - Diagram the event flows; document idempotency and how duplicate and poison messages are handled.
   - Document schema versioning and backward compatibility between producers and consumers.

76. Logging & Monitoring Architecture
   - Document how logs, metrics and traces are produced, shipped, stored and viewed (libraries, agents, OpenTelemetry, and backends such as CloudWatch, Datadog, Grafana, Prometheus, Sentry).
   - Document log format, levels, correlation or request IDs, retention, and redaction of personal data and secrets.
   - List the dashboards, alerts and on-call routing that actually exist, separately from recommended ones.
   - Diagram the telemetry pipeline.

77. Error Handling Architecture
   - Document the error model: error types or exception hierarchy, and where errors are caught, translated, logged and returned.
   - Document the API error response format, the status-code mapping, and which messages users see versus which stay internal.
   - Document retries, timeouts, circuit breakers and fallbacks, and what is logged or alerted for each class of error.
   - Flag swallowed exceptions, broad catch-alls, and stack traces or internal details leaking to clients.

78. Disaster Recovery Architecture
   - State the RTO and RPO if they are defined; otherwise say that none are defined.
   - Document backups (what, where, frequency, retention, encryption), replication, multi-zone or multi-region setup, failover, and whether restores are tested.
   - Write step-by-step recovery runbooks for the most likely disasters: database loss, region or provider outage, credential compromise, accidental deletion, bad deploy.
   - Separate implemented mechanisms from recommendations; never claim recovery capability that configuration doesn't show (see rule 52).

79. Scalability Strategy
   - Identify the scaling dimensions (users, requests, data volume, tenants, jobs) and the current limits, with evidence.
   - Document stateless versus stateful components and the scaling configuration in place (autoscaling rules, replicas, worker counts, pool sizes).
   - Describe what breaks first at each growth stage (for example 10x and 100x current load) and the step that addresses it.
   - Label every capacity figure as measured or estimated.

80. Cost Architecture
   - Identify the cost drivers: compute, storage, data transfer, managed services, third-party and LLM API usage, and licences.
   - Map each driver to the component that causes it and its billing unit (per request, GB, token, seat, hour).
   - Use prices from official sources with the date checked; when usage is unknown, give the formula rather than invented totals.
   - Document cost controls in place (budgets, alerts, quotas, caching, batching) and list savings opportunities as recommendations.

81. Technical Debt Analysis
   - Collect evidence: TODO/FIXME/HACK comments, deprecated or outdated dependencies, dead code, duplicated logic, missing tests, disabled lint rules and known workarounds.
   - For each item: location, impact, risk, effort (S/M/L) and suggested fix.
   - Prioritize by impact and risk; separate quick wins from structural work.
   - Stay factual and neutral: describe the code, not the people who wrote it.

82. Security Threat Model
   - Identify assets, actors, entry points and trust boundaries from the architecture.
   - Apply a structured method such as STRIDE to each component or data flow; list each threat with likelihood, impact, existing mitigations and gaps.
   - Include a data-flow diagram that shows the trust boundaries.
   - Never include working exploit details or real secrets; reference files and lines, and state the residual risk.

83. Performance Bottleneck Analysis
   - Find bottlenecks from evidence: query plans, profiles, load tests, metrics, logs, algorithmic complexity, N+1 queries, synchronous external calls, large payloads, missing pagination.
   - For each: location, symptom, cause, impact (measured or labelled as estimated) and fix options.
   - When something hasn't been measured, explain how to measure it.
   - Prioritize by user-facing impact.

84. Future Architecture
   - Describe the target architecture that follows from the roadmap, scalability strategy, threat model and technical debt, as a diagram labelled "proposed".
   - Show incremental migration steps from the current architecture to the target, with dependencies and risks.
   - Justify each change with a current, evidenced limitation; avoid speculative rewrites.
   - Record significant choices as ADRs (rule 37).

85. Documentation Change Checklist
   - Map code areas to the documents that must change with them (for example `src/auth/**` → `docs/SECURITY.md` role matrix).
   - Provide a pull-request checklist covering new endpoints, environment variables, tables and migrations, dependencies, integrations, roles and permissions, and infrastructure changes.
   - Suggest automation where it fits: CODEOWNERS for docs, a PR template checkbox, a CI check that every environment variable is documented, `tbls diff` for schema drift, link checking.
   - Place the checklist where contributors will see it (`CONTRIBUTING.md` or the PR template), and edit those files only when the user asks.
