# doc-maker

Two Claude skills that write professional, evidence-based documentation for software, AI/ML, data and engineering projects.

| Skill | Covers | Rules |
|-------|--------|-------|
| `doc-maker` | README, overview, problem definition, architecture, tech stack, project structure, features, use cases, API, AI/ML pipeline, data flow, security, deployment, install/config, performance, reliability, testing, observability, ADRs, competitor comparison, limitations, roadmap, glossary, Mermaid diagrams | 1-40 |
| `database-docs` | Database type and schema, data dictionary, ER diagram from the real schema, relationships and cascades, indexes, normalization, queries, migrations, seed data, transactions, security, backup/recovery, lifecycle, app-to-database mapping, trade-offs | 41-60 |

The rules are a checklist, not a template: Claude inspects the repository first, applies only the rules that fit the project, marks assumptions, and never invents features or exposes secrets.

## Install

> Replace `<owner>` below with the GitHub account that hosts this repository.

### Claude Code (plugin)

```
/plugin marketplace add <owner>/doc-maker
/plugin install doc-maker@doc-maker
```

### Claude Code (manual)

Copy the skill folders into your personal skills directory:

```bash
git clone https://github.com/<owner>/doc-maker.git
cp -r doc-maker/skills/doc-maker doc-maker/skills/database-docs ~/.claude/skills/
```

For a single project, copy them into `<project>/.claude/skills/` instead.

### Claude.ai / Claude Desktop

Zip each folder in `skills/` (the zip must contain the folder, with `SKILL.md` inside it), then upload it under **Settings > Capabilities > Skills**.

## Usage

Ask Claude in plain language. The skills trigger on their own:

- "Write a README for this repo"
- "Document the architecture of this project"
- "Generate an ER diagram and data dictionary for our database"
- "Write executive-level documentation for this service"

## Repository layout

```
.claude-plugin/
  plugin.json        Plugin manifest
  marketplace.json   Marketplace entry, so the repo can be added with /plugin marketplace add
skills/
  doc-maker/SKILL.md       Rules 1-40
  database-docs/SKILL.md   Rules 41-60
```

## License

[MIT](LICENSE)
