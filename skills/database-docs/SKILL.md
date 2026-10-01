---
name: database-docs
description: Document a project's database evidence-first - database type/version, schema and data dictionary, ER diagram (Mermaid) generated from the real schema, relationships and cascade behavior, indexes and the queries they serve, normalization, important queries and bottlenecks, migrations, seed data, transactions/integrity, security, backup/recovery, lifecycle, app-to-database mapping and trade-offs. Use when documenting any project that stores data (SQL, NoSQL, SQLite, Postgres, MySQL, MongoDB, Redis, vector DBs), when asked for an ER diagram, schema or data dictionary, or when doc-maker needs its database section.
---

# database-docs

## Purpose
Document a project's data layer so that another developer can understand, safely change, operate and scale it.
Companion to the **doc-maker** skill (rules 1-40) and the **architecture-docs** skill (rules 61-85); rules numbered 41-60 continue that numbering.

## How to apply (read first)

1. **Find every source of truth.** Schema/DDL files, migrations, ORM models, raw SQL in the codebase,
   repository/data-access code, API models, configuration (connection strings, pool sizes), seed scripts, and
   deployment files (managed DB services, backups).
2. **Introspect read-only when a database is available.** Examples: SQLite `sqlite_master`, `PRAGMA table_info`,
   `PRAGMA foreign_key_list`, `PRAGMA index_list`, `PRAGMA journal_mode`; Postgres `information_schema`,
   `pg_indexes`, `\d+`; `EXPLAIN` / `EXPLAIN QUERY PLAN` on the queries the code actually runs. **Never write,
   migrate, or delete data** while documenting, and never print credentials or real personal data (use counts and
   synthetic examples).
3. **Validate (rule 60).** When the schema file, the live database and the code disagree (e.g. a column the code
   never uses, an FK in the ORM but not in the DDL, a query that can't use an index), document the discrepancy
   instead of silently picking one.
4. **Relevance.** Apply each rule only when it applies; state "not present" plainly (e.g. "No migration tool:
   schema is applied with CREATE TABLE IF NOT EXISTS") and describe the consequence rather than skipping it.
5. **Separate implemented from recommended** (backups, indexes, encryption): label recommendations as such and
   back them with evidence (query plans, row counts, measured timings).
6. **Output.** Usually `docs/DATABASE.md`, linked from the README. Mermaid `erDiagram` for the ER diagram; relations
   must match actual foreign keys (or be marked "logical, not enforced").

## Rules

41. Database Structure
   - Analyze the complete database architecture.
   - Document database type, version, schema, tables/collections, relationships, indexes, constraints, and extensions.
   - Explain why the selected database technology is appropriate.

42. Database Schema Documentation
   - Document every important table/collection.
   - Include: table/collection name, purpose, columns/fields, data types, primary keys, foreign keys, nullable
     fields, default values, unique constraints, check constraints.
   - Explain important relationships between entities.

43. Database ER Diagram
   - Generate a professional ER diagram from the actual schema.
   - Show entities, attributes, PKs, FKs, and cardinality.
   - Ensure the diagram matches the implementation.
   - Never invent relationships that are not present in the database.

44. Database Relationships
   - Explain one-to-one, one-to-many, and many-to-many relationships.
   - Explain junction/association tables where applicable.
   - Document cascading behavior such as CASCADE, SET NULL, and RESTRICT.
   - Explain why important relationships were designed that way.

45. Database Indexing
   - Identify existing indexes.
   - Explain what queries each important index optimizes.
   - Identify potentially missing indexes when evidence supports it.
   - Explain composite, unique, partial, full-text, or specialized indexes where applicable.

46. Database Normalization
   - Analyze the schema's normalization level where meaningful.
   - Identify normalization decisions and intentional denormalization.
   - Explain the trade-off between consistency, query complexity, and performance.

47. Database Query Documentation
   - Document important database queries.
   - Explain complex joins, aggregations, transactions, filtering, pagination, and sorting.
   - Identify expensive queries or potential performance bottlenecks.

48. Database Migration Structure
   - Document the migration system.
   - Explain migration files, versioning, rollback strategy, and schema evolution.
   - Explain how developers should safely modify the database schema.

49. Seed & Sample Data
   - Document database seed scripts.
   - Explain required initial data.
   - Provide commands for creating/resetting development databases where applicable.
   - Never expose real production data.

50. Transactions & Data Integrity
   - Identify operations requiring transactions.
   - Explain transaction boundaries.
   - Document ACID considerations, isolation levels, locking, optimistic/pessimistic concurrency, and consistency mechanisms where applicable.

51. Database Security
   - Document database authentication and authorization.
   - Explain roles and permissions.
   - Identify sensitive columns/data.
   - Explain encryption, secret management, network restrictions, and access controls where applicable.
   - Never expose database credentials.

52. Database Backup & Recovery
   - Document backup strategy when available.
   - Explain backup frequency, retention, restore procedures, replication, and disaster-recovery mechanisms.
   - Clearly distinguish implemented mechanisms from recommended future improvements.

53. Database Performance
   - Analyze query performance, connection pooling, caching, indexing, pagination, batching, and connection limits.
   - Identify likely bottlenecks based on the actual implementation.
   - Provide concrete optimization recommendations where justified.

54. Database Lifecycle
   - Explain the complete data lifecycle: Create → Validate → Store → Read → Update → Archive/Delete.
   - Document retention and deletion behavior where applicable.
   - Explain soft deletion vs hard deletion when used.

55. Database-to-Application Mapping
   - Map database entities to application models, ORM models, repositories, services, and API endpoints.
   - Show how data moves from API request → business logic → database → response.

56. Database Architecture Diagram
   - When appropriate, generate a dedicated database architecture diagram showing: application, API, ORM/database
     layer, connection pool, cache, database, read replicas, backup/storage, external data sources.
   - Only include components actually present or explicitly marked as proposed.

57. Data Dictionary
   - Generate a structured data dictionary for important entities.
   - Include field name, type, description, constraints, example value, and sensitivity classification where applicable.

58. Database Trade-offs
   - Explain why the project uses PostgreSQL, MySQL, MongoDB, Redis, SQLite, vector databases, graph databases, or another storage technology.
   - Compare relevant alternatives only when useful.
   - Explain consistency, scalability, query model, operational complexity, and performance trade-offs.

59. Multi-Database Architecture
   - If multiple databases/storage systems are used, explain the responsibility of each.
   - Example: PostgreSQL → transactional data; Redis → caching/session data; S3 → files/object storage;
     Vector DB → embeddings; Elasticsearch → search/indexing.
   - Explain synchronization and data-flow relationships between them.

60. Database Documentation Validation
   - Cross-check database documentation against: schema files, ORM models, migration files, SQL files,
     repository/data-access code, API models, configuration.
   - Flag discrepancies instead of silently guessing.
