---
name: doc-maker
description: Write or update evidence-based project documentation - README, overview, features, quick start, configuration, architecture summary, tech-stack rationale, API/CLI reference, AI/ML pipeline, testing, ADRs, limitations, roadmap, competitor comparison, glossary, Mermaid diagrams - for developer, product or executive readers. Use when the user wants documentation written, rewritten, or checked against the code. Not for answering questions about how code works. Also load database-docs for data/schema docs and architecture-docs for in-depth security, infrastructure and operations docs.
---

# doc-maker

Write documentation that describes the project as it is, verified against the code, at the length the reader needs.
Companions: **database-docs** (rules DB1-DB12) and **architecture-docs** (rules A1-A19). Rule IDs here are D1-D20.

## Process

0. **Preferences.** If `.doc-maker.md` exists at the repository root, read it first and follow it (audience, tone,
   sections to skip, length, terms). It overrides the defaults below, never the safety rules.
1. **Audience and scope.** Decide who reads it (developers, product, executives, open-source users) and what was asked
   for. If the request is ambiguous about scope, write the README only and offer the rest.
2. **Collect evidence with the script.** Run `python3 <this skill's directory>/scripts/evidence.py <command> <repo>`
   for `inventory`, then `env`, `deps` and `routes` as relevant (`docs` when updating existing docs). Output is JSON
   with file:line locations. Open the files it points to before writing about them. Use `python` if `python3` isn't found. If Python isn't available, gather
   the same facts by reading manifests, config and entry points.
3. **Stay read-only.** Never run commands that change data, infrastructure or git history (migrations, deploys,
   writes, commits). Never print secret values: refer to secrets by name or file:line.
4. **Select rules by tier.** Tier 1: always. Tier 2: only when the project has the thing (state "not present" in
   one line when its absence matters). Tier 3: only when the user asks. Load **database-docs** if the project stores
   data, and **architecture-docs** if the user wants security, infrastructure or operations depth.
5. **Write** using the templates in `references/` when they fit:
   `readme-template.md` (README), `adr-template.md` (D13). Follow the project's existing doc layout if it has one;
   otherwise README + focused files under `docs/`.
6. **Respect length budgets.** README: ~1,200 words for a small project, ~2,000 for a large one. Each `docs/*.md`:
   ≤ 2,500 words unless the user asks for more. Cut before you exceed them; link instead of repeating.
7. **Updating existing docs:** run `evidence.py docs`, check every claim in the current docs against the code, and list
   the mismatches (outdated, missing, wrong, unverifiable) before fixing them. Keep correct content and structure.
8. **Quality check.** Run `evidence.py docs` on what you wrote: zero broken links or anchors, every env var and command
   exists. Re-check numbers, paths and names. Use one name per component across all files and diagrams.
9. **Hand over and ask for feedback.**
   - List each file and section written with an **evidence score**: *high* (every claim checked in code or by a
     command), *medium* (some labelled assumptions), *low* (mostly inferred). State the audience assumed.
   - List assumptions and open questions.
   - Ask which sections to improve. Revise **only** the sections the user names, then summarise what changed.
   - If the user states a lasting preference ("always skip roadmap", "shorter"), offer to save it in `.doc-maker.md`;
     write that file only with their approval and never put secrets in it.
   - Don't commit or publish unless asked.

## Writing standards (apply to every rule)

- **Evidence:** every technical claim traces to a file, config value, command output or cited source. Label anything
  else "Assumption:". Never describe features, endpoints, flags or tables that don't exist.
- **Honesty:** no "best", "fast", "secure", "production-ready" without evidence. Limitations are stated plainly.
- **Readers:** developers get precise commands and file paths; product readers get workflows and value; executives get
  impact, risks and one high-level diagram.
- **Format:** short paragraphs, tables for comparisons, fenced code for commands and config, GitHub callouts
  (`> [!WARNING]`) for warnings. Mermaid diagrams only when they show what text can't; every label matches the code.
- **Secrets:** placeholders only (`<YOUR_API_KEY>`), never real values, even from example files.

## Rules

Each rule: **Look for** (evidence and where) · **Verify** (before writing) · **Output** (where and how long).

**D1. Overview and problem** · Tier 1
- Look for: README draft, package descriptions, entry points, main user-facing flow.
- Verify: the described purpose matches what the code does end to end.
- Output: README opening. One sentence on what it is and for whom, 2-4 on the problem and approach. For the problem:
  current pain, why existing approaches fall short, root cause; skip what you can't support.

**D2. Who it's for, when to use it, when not to** · Tier 2 (Tier 1 for open-source libraries and tools)
- Look for: target users implied by interfaces (CLI, API, UI), configuration options, limits in code.
- Verify: "when not to use" items come from real limits (unsupported platforms, scale, missing features).
- Output: short README section or `docs/USE_CASES.md` with 2-5 realistic scenarios and personas.

**D3. Features** · Tier 1
- Look for: routes, commands, UI pages, public functions, feature flags.
- Verify: each feature maps to code you opened; mark experimental or flag-gated features as such.
- Output: 3-8 README bullets. Optional `docs/FEATURES.md`: purpose, inputs, outputs, dependencies; core vs optional.

**D4. Quick start and installation** · Tier 1
- Look for: `evidence.py inventory` + `deps` (runtime and versions), lockfile tool, scripts in package.json/Makefile,
  docker-compose services, setup scripts, seed commands.
- Verify: every command exists (`evidence.py docs` flags missing npm scripts and make targets); prerequisites match
  version files (`.nvmrc`, `.python-version`, `engines`, `go.mod`).
- Output: README: prerequisites, clone, install, configure, run, expected result. Add troubleshooting for the setup
  failures the code makes likely (missing env var, port in use, database not running).

**D5. Configuration** · Tier 1 when the project reads env vars or config files
- Look for: `evidence.py env` (`used_in_code`, `missing_from_examples`, `env_files_in_repo`), config files.
- Verify: required vs optional from code (default present or not); flag variables used but undocumented.
- Output: table of variable, required, default, purpose, with placeholders only. If `env_files_warning` is set, tell the
  user privately that a real `.env` is in the repo; don't print its contents.

**D6. Architecture summary and data flow** · Tier 1
- Look for: entry points, top-level modules, services in compose/manifests, external calls, storage.
- Verify: every box in the diagram exists in code or config; every arrow is a real call or data path.
- Output: README: 3-5 sentences + one Mermaid diagram (input → processing → storage → output). Depth goes to
  architecture-docs (A1-A19) in `docs/ARCHITECTURE.md`.

**D7. Technology stack rationale** · Tier 2
- Look for: `evidence.py deps`, config, ADRs, commit messages that introduced each major dependency.
- Verify: each technology is actually used (imported or configured), not just installed.
- Output: table of technology, role in this project, why (evidence or labelled assumption), realistic alternatives.
  Major technologies only (frameworks, databases, queues, cloud, AI models), not every package.

**D8. Project structure** · Tier 2
- Look for: directory tree (depth 2-3), module boundaries, naming patterns (MVC, layered, hexagonal, feature folders).
- Verify: each directory's described responsibility matches its contents.
- Output: annotated tree with one line per important directory or file; name the architectural pattern if clear.

**D9. Interfaces: API, CLI, library** · Tier 2
- Look for: `evidence.py routes`, OpenAPI/GraphQL schemas, CLI argument parsers, exported functions, auth middleware.
- Verify: open each handler; method, path, parameters, auth requirement, status codes and response shape come from
  code. Routes from the script are heuristics; confirm prefixes and mounts.
- Output: `docs/API.md` (or README section for small APIs) with one example per endpoint or command. If an OpenAPI
  spec exists, link it and document flows instead of duplicating it. Endpoint ↔ table mapping: database-docs DB10.

**D10. AI/ML pipeline** · Tier 2
- Look for: datasets and loaders, preprocessing, model definitions or API calls, prompts, embeddings and vector stores,
  RAG retrieval, agents and tools, evaluation scripts, inference serving.
- Verify: model names, parameters and metrics come from code, config or result files; unmeasured metrics are said to
  be unmeasured.
- Output: `docs/ML.md`: pipeline diagram, why each model or approach, evaluation method and results, hallucination
  risks, fallbacks, limitations.

**D11. Testing** · Tier 2
- Look for: `evidence.py inventory` (`tests`), test configs, CI test steps, coverage config.
- Verify: test commands run, or exist in scripts; describe what each layer actually covers.
- Output: README section or `docs/TESTING.md`: layers (unit, integration, e2e, evals), commands, notable gaps.

**D12. Deployment, security and operations summary** · Tier 2
- Look for: `evidence.py inventory` (`containers`, `ci`, `iac`, `platform`), auth middleware, logging setup.
- Verify: as in the matching architecture-docs rules.
- Output: one short README paragraph each for how it's deployed, how access is controlled, and how it's monitored, with
  links to the depth docs. Write the depth only through architecture-docs (A1-A19), never twice.

**D13. Design decisions (ADRs)** · Tier 2 when there is evidence; Tier 3 otherwise
- Look for: existing ADRs, commit messages, PR descriptions, comments explaining "why", config choices.
- Verify: each decision is visible in code or history; reconstructed reasoning is labelled an assumption.
- Output: `references/adr-template.md` format in `docs/DECISIONS.md`: context, problem, options, decision, rationale,
  trade-offs, consequences. 3-7 records for a typical project.

**D14. Limitations and known issues** · Tier 1
- Look for: TODO/FIXME comments, open issues if available, unsupported cases in code, missing tests, stubs.
- Verify: each item is current (still in the code).
- Output: README bullet list. Never omit a known limitation to make the project look better.

**D15. Roadmap** · Tier 3
- Look for: issues, milestones, TODOs, ROADMAP files, the limitations from D14.
- Verify: separate done, in progress (open branches or PRs), planned (documented) and potential (your suggestions).
- Output: short list ordered by impact; label suggestions as suggestions.

**D16. Competitor comparison** · Tier 3
- Look for: web search for alternatives; the project's own README claims.
- Verify: every fact about another product has a cited source and a date; when no reliable source exists, say so.
- Output: `docs/COMPARISON.md`: matrix of meaningful dimensions, including rows where alternatives win; facts
  separated from interpretation; no "best" or "better" without evidence.

**D17. Glossary** · Tier 2 when the project has domain terms, acronyms or internal names
- Look for: model and class names, enum values, acronyms in code and docs.
- Verify: definitions match how the code uses the term.
- Output: `docs/GLOSSARY.md` or README section; one or two sentences per term.

**D18. Diagrams** · applies whenever a rule produces one
- Choose the type for the question: flowchart (structure, flow), `sequenceDiagram` (interactions over time),
  `stateDiagram-v2` (lifecycles), `erDiagram` (data).
- Verify: names match code and other diagrams; ~15 nodes or edges at most per diagram, otherwise split.
- Output: Mermaid in Markdown, with a one-line caption saying what the diagram answers.

**D19. Maintainability of the docs** · Tier 2
- Look for: which code areas each doc depends on.
- Output: a short "Keeping these docs current" note: which files to update when which code changes. For a full
  checklist and CI checks, use architecture-docs A19.

**D20. Final check** · always
- A new developer reading the result can answer: what is it, what problem does it solve, who is it for, how does it
  work, how do I run it, how is it configured, what are its limits. Anything missing from that list is either added
  or explicitly marked "not applicable" with the reason.
