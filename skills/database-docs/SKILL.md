---
name: database-docs
description: Document a project's database evidence-first - database type and choice, schema and data dictionary, ER diagram (Mermaid) built from real foreign keys, relationships and cascades, normalization, indexes and the queries they serve, migrations, seed data, transactions and integrity, sensitive columns, endpoint-to-table mapping, data lifecycle, backup and restore. Use when asked for an ER diagram, schema docs, a data dictionary or database documentation, or when doc-maker documents a project that stores data (SQL, NoSQL, SQLite, Postgres, MySQL, MongoDB, Redis, vector stores).
---

# database-docs

Document the data layer so another developer can understand it, change it safely and operate it.
Companions: **doc-maker** (D1-D20) and **architecture-docs** (A1-A19). Rule IDs here are DB1-DB12.

## Process

1. **Collect evidence with the script.** Run `python3 <this skill's directory>/scripts/evidence.py schema <repo>`
   (SQLite files, SQL/migrations including `ALTER TABLE` foreign keys, Prisma, Django, SQLAlchemy, SQLModel), then
   `routes` for DB10 and `env` for connection settings. Then read the ORM models, migrations, raw SQL and data-access
   code the output points to. Use `python` if `python3` isn't found. If Python isn't available, read those files directly.
2. **Introspect read-only, only if a development database is available**: SQLite `PRAGMA table_info / foreign_key_list
   / index_list`, Postgres `information_schema` and `pg_indexes`, `EXPLAIN` on queries the code runs. Never write,
   migrate or delete data; never print credentials or real rows (use counts and synthetic examples).
3. **Validate across sources.** Compare migrations, ORM models, the live schema and the queries in code. When they
   disagree (FK in the ORM but not in SQL, a column the code never uses, a query no index can serve), **report the
   discrepancy**; never silently pick one.
4. **Select rules by tier.** Tier 1: always. Tier 2: when the project has the thing; when its absence matters (no
   migrations, no backups), say so in one line with the consequence. Tier 3: on request.
5. **Write** with `references/data-dictionary-template.md`, usually in `docs/DATABASE.md` (≤ 2,500 words; split
   per domain beyond ~15 tables). Label recommendations (new index, backup policy) separately from what exists, and
   back them with evidence (query plan, row counts, measured timing).
6. **Hand over** with an evidence score per section (*high* / *medium* / *low*), the discrepancies found, assumptions
   and open questions; ask which sections to improve and revise only those.

## Rules

Each rule: **Look for** · **Verify** · **Output**.

**DB1. Database overview and technology choice** · Tier 1
- Look for: engines and versions (compose images, IaC, drivers in `evidence.py deps`), extensions, every storage system
  (relational, cache, object storage, search, vector store), connection and pool settings.
- Verify: each store is actually used by code, not just configured.
- Output: what each store holds and why it fits (consistency, query model, scale, operational cost); compare
  alternatives only when useful. With more than one store, add a Mermaid diagram (app → ORM/pool → stores, replicas,
  backups) showing only components that exist or are labelled "proposed", and explain how data syncs between them.

**DB2. Schema and data dictionary** · Tier 1
- Look for: `evidence.py schema` output; model files for descriptions and enums.
- Verify: types, nullability, defaults, PK/FK/unique/check constraints match the migrations or live schema.
- Output: per important table: purpose, then the dictionary table from the template (field, type, null, default,
  constraints, description, synthetic example, sensitivity).

**DB3. ER diagram and relationships** · Tier 1
- Look for: foreign keys from every source in `evidence.py schema`, junction tables, cascade rules.
- Verify: draw only relationships backed by a foreign key; relationships the code relies on without one are labelled
  "(logical, not enforced)". Cardinality matches nullability and uniqueness.
- Output: Mermaid `erDiagram` (overview + per-domain diagrams for large schemas). Explain one-to-one, one-to-many and
  many-to-many relationships, junction tables, and ON DELETE / ON UPDATE behaviour (CASCADE, SET NULL, RESTRICT) with
  why it matters.

**DB4. Design and normalization** · Tier 2
- Look for: repeated columns, JSON blobs, denormalized counters or copies, materialized views.
- Verify: intentional denormalization is backed by a comment, ADR or read-path need.
- Output: short section: normalization level where meaningful, intentional denormalization and its trade-off
  (consistency vs query cost vs speed).

**DB5. Indexes and query performance** · Tier 2
- Look for: indexes (schema output), the queries the code runs (ORM calls, raw SQL), pagination and sorting, N+1
  patterns, pool size and connection limits, caching of query results.
- Verify: with a dev database, `EXPLAIN` the important queries; otherwise state which index each query should use and
  label it unverified.
- Output: table of index, columns, type (unique, composite, partial, full-text, vector), query it serves. Then likely
  bottlenecks and missing indexes, each as a labelled recommendation with its evidence.

**DB6. Migrations and safe schema change** · Tier 2
- Look for: migration tool and folder (Alembic, Prisma, Django, Rails, Flyway, Liquibase, Knex), naming and
  versioning, down migrations, how migrations run in CI/deploy.
- Verify: commands exist; whether rollbacks are actually written.
- Output: how to create, apply and roll back a migration; rules for safe changes (add nullable first, backfill,
  then constrain; avoid long locks). If there is no migration system, say how the schema is applied and the risk.

**DB7. Seed data and development database** · Tier 2
- Look for: seed scripts, fixtures, factories, compose database services, reset commands.
- Verify: commands exist; seed data is synthetic.
- Output: commands to create, seed and reset a local database; required initial data (admin user, lookup tables).
  Never include real production data.

**DB8. Transactions and integrity** · Tier 2
- Look for: transaction blocks (`BEGIN`, `atomic()`, `$transaction`, `session.begin()`), row locks (`FOR UPDATE`),
  optimistic version columns, isolation settings, constraints enforcing invariants.
- Verify: multi-write operations without a transaction are findings, not footnotes.
- Output: which operations are transactional and where the boundaries are; isolation level if set; how concurrency
  conflicts are handled; gaps.

**DB9. Database security and sensitive data** · Tier 2
- Look for: database users and roles, grants, row-level security, network exposure (ports, security groups), TLS,
  encryption at rest, how credentials are supplied (`evidence.py env`), columns with personal data, tokens or hashes.
- Verify: credentials are never in code or committed files; if they are, report file:line, never the value.
- Output: access model, sensitive columns with classification, protections in place, gaps as recommendations.

**DB10. Application ↔ database mapping** · Tier 2
- Look for: `evidence.py routes` + the handlers, services and repositories behind each route; models per table.
- Verify: open each important handler and follow it to the queries; note transactions and N+1 patterns.
- Output: entity view (table → model → repository/service → endpoints) and endpoint view (endpoint → reads → writes →
  transaction), using the API ↔ database table format. Show one request path (API → business logic → database →
  response) as a diagram.

**DB11. Data lifecycle and retention** · Tier 2
- Look for: create, update and delete paths; soft-delete columns (`deleted_at`, `is_active`); archival jobs, TTLs,
  retention or GDPR deletion code.
- Verify: whether deletes are hard or soft per entity; whether retention is enforced or only documented.
- Output: Create → Validate → Store → Read → Update → Archive/Delete for the main entities; retention rules and gaps.

**DB12. Backup and restore** · Tier 2 (state "no backup configuration found" when none exists)
- Look for: managed-database backup settings in IaC or platform config, backup jobs, dump scripts, replication.
- Verify: separate configured mechanisms from intentions; whether a restore has ever been tested.
- Output: what is backed up, frequency, retention, where, restore steps. Recommendations labelled as such.
  Disaster-recovery architecture beyond the database is architecture-docs A14.
