---
name: doc-maker
description: Create professional, evidence-based documentation for software, AI/ML, data and engineering projects - README, architecture docs, feature/use-case docs, tech-stack rationale, ADRs, competitor comparison, deployment/security/testing/observability docs, glossary, Mermaid diagrams. Use when the user asks to document a project, write or rewrite a README, explain a codebase's architecture, or produce developer/product/executive documentation. Applies only the rules relevant to the project at hand; for database/schema documentation also use the database-docs skill, and for in-depth architecture, security, infrastructure and operations documentation the architecture-docs skill.
---

# doc-maker

## Purpose
Create professional, comprehensive, developer-friendly documentation for software, AI/ML, data, and engineering projects.

## How to apply (read first)

The rules below are a **checklist, not a template**. Apply each rule only when the project actually has the thing it
talks about; say so explicitly when a section does not apply (e.g. "No HTTP API: the project exposes a CLI and a
Python API instead"). Never pad documentation with sections the project doesn't need.

1. **Audience and scope.** Decide who reads it (developers, product/business users, executives; rule 33) and what
   was asked for (a README only, or a full documentation set). State the audience in one line to the user when
   handing the docs over.
2. **Evidence first (rule 31).** Before writing any technical claim, inspect the repository: file tree, entry
   points, dependency files, configuration, schemas/migrations, API routes, tests, CI and deployment files, and git
   history if useful. Prefer verifiable, read-only checks (grep for usages, run tests, `EXPLAIN` queries, `--help`
   output) over assumptions. Mark anything unverifiable as an assumption.
3. **Relevance pass.** Walk rules 1-40 and decide for each: applies / partially / not applicable (with reason).
   If the project has a database, also load the **database-docs** skill for rules 41-60.
   If the project needs architecture or operations depth (auth model, role matrix, deployment/cloud/CI-CD, integrations,
   caching, queues, monitoring, disaster recovery, cost, threat model, technical debt), also load the
   **architecture-docs** skill for rules 61-85.
4. **External facts.** For competitor analysis, pricing, hosting limits or other outside facts, research with web
   search and cite sources. If reliable information isn't available, say so; never invent it.
5. **Layout.** Default: a `README.md` that gives the overview and quick start and links to focused documents under
   `docs/` (for example `ARCHITECTURE.md`, `DATABASE.md`, `ML.md`, `OPERATIONS.md`, `DECISIONS.md`,
   `COMPARISON.md`, `GLOSSARY.md`). Create only the documents the project warrants. Follow the project's existing
   documentation conventions if it has them.
6. **Diagrams.** Use Mermaid (renders on GitHub) only where a diagram explains something text can't (rules 27, 28).
7. **Honesty.** Document limitations, known issues, optimistic metrics and dead code plainly (rule 25). Never
   describe features that don't exist. Never include real secrets; use placeholders (rule 18).
8. **Quality check before handing over (rule 34).** Re-verify numbers, commands, paths, links and names against the
   code; make terminology consistent across files (rule 32).
9. **Don't commit or publish** documentation unless the user asks.

## Rules

1. Make Good Documentation
   - Create clean, professional, well-structured documentation.
   - Use clear headings, sections, tables, diagrams, examples, and consistent formatting.
   - Write for both technical and non-technical readers where appropriate.

2. Explain the Project
   - Explain what the project does.
   - Explain the core idea and workflow.
   - Explain the problem being solved.
   - Explain how the complete system works from input to output.
   - Include a concise project overview before going into technical details.

3. Pain Points & Problem Definition
   - Clearly identify the existing pain points.
   - Explain how the problem is currently handled.
   - Explain limitations of existing approaches.
   - Explain why the proposed solution is necessary.
   - Distinguish the problem, symptoms, root causes, and consequences.

4. Why, When & How to Use
   - Explain WHY someone should use the project.
   - Explain WHEN the project is appropriate.
   - Explain WHEN it should NOT be used.
   - Explain HOW to use it.
   - Provide practical use cases and example scenarios.

5. ER Diagrams & Data Architecture
   - Analyze the project's data model.
   - Generate professional ER diagrams when databases are involved.
   - Show entities, attributes, primary keys, foreign keys, and relationships.
   - Explain cardinality and important database constraints.
   - Include the database design rationale.

6. System Architecture
   - Create a clear system architecture diagram.
   - Show frontend, backend, APIs, databases, caches, queues, AI/ML services, external services, storage, authentication, and infrastructure where applicable.
   - Explain data flow between components.
   - Explain why each major architectural component exists.
   - Document important architectural decisions and trade-offs.

7. Technology Stack Explanation
   - Document every major technology used.
   - Explain WHY each technology was selected.
   - Explain alternatives that could have been used.
   - Identify the responsibility of each technology in the system.
   - Avoid listing technologies without explaining their purpose.

8. Project Structure
   - Analyze the repository structure.
   - Generate a professional folder/file structure section.
   - Explain the responsibility of important directories and files.
   - Identify separation of concerns between modules.
   - Explain architectural patterns used by the codebase.

9. Competitor Analysis
   - Identify relevant competitors and alternative solutions.
   - Compare functionality, architecture, target users, limitations, pricing/model where reliable information is available, and differentiating capabilities.
   - Clearly distinguish documented facts from interpretation.
   - Explain where the project differentiates itself.
   - Do not make unsupported claims such as "best" or "better" without evidence.

10. Feature Breakdown
    - Document the project's major features.
    - Explain each feature's purpose, workflow, inputs, outputs, and dependencies.
    - Separate core features from optional/supporting features.
    - Include feature-to-problem mapping where useful.

11. User & Use-Case Documentation
    - Identify target users/personas.
    - Document realistic use cases.
    - Describe user workflows.
    - Include use-case diagrams when useful.
    - Explain the value delivered to each user type.

12. API Documentation
    - Document important APIs and endpoints.
    - Include HTTP method, endpoint, parameters, request body, response structure, authentication requirements, status codes, and examples.
    - Explain important API flows.
    - Keep API documentation synchronized with the actual implementation when source code is available.
    - If there is no HTTP API, document the interfaces that do exist (CLI commands, public functions/classes, events) instead.

13. AI/ML Documentation
    - For AI/ML projects, explain the complete ML/AI pipeline.
    - Document datasets, preprocessing, feature engineering, models, embeddings, vector databases, RAG pipelines, agents, prompts, inference, evaluation, and deployment where applicable.
    - Explain why each model/approach was selected.
    - Document limitations, hallucination risks, evaluation methodology, and fallback mechanisms.

14. Data Flow Documentation
    - Explain how data moves through the system.
    - Document input → processing → storage → retrieval → output.
    - Create data-flow diagrams when useful.
    - Identify transformations, APIs, queues, caches, and persistence layers.

15. Security Documentation
    - Document authentication and authorization.
    - Explain roles and permissions.
    - Identify sensitive data.
    - Document encryption, secrets management, input validation, rate limiting, and common security controls where applicable.
    - Identify potential security risks and mitigations.

16. Deployment & Infrastructure
    - Explain how the project is deployed.
    - Document local development, staging, and production environments.
    - Explain Docker, cloud services, CI/CD, databases, networking, domains, storage, and monitoring where applicable.
    - Provide deployment architecture diagrams when useful.

17. Installation & Quick Start
    - Provide prerequisites.
    - Provide installation steps.
    - Provide environment-variable documentation.
    - Provide database/setup commands where required.
    - Provide a minimal Quick Start that gets a new developer running quickly.
    - Include troubleshooting for common setup failures.

18. Configuration Documentation
    - Document configuration files and environment variables.
    - Explain required vs optional configuration.
    - Never expose real secrets, API keys, tokens, passwords, or credentials.
    - Provide safe placeholder examples.

19. Performance & Scalability
    - Explain expected bottlenecks.
    - Document caching, database optimization, asynchronous processing, queues, batching, concurrency, and horizontal/vertical scaling where applicable.
    - Explain how the architecture can evolve as usage increases.
    - Document measurable performance characteristics when available.

20. Reliability & Failure Handling
    - Document failure points.
    - Explain retries, timeouts, fallbacks, circuit breakers, validation, error handling, and graceful degradation where applicable.
    - Include important failure scenarios and expected system behavior.

21. Testing Documentation
    - Document unit, integration, API, end-to-end, ML evaluation, and performance tests where applicable.
    - Explain what each testing layer validates.
    - Provide commands for running tests.
    - Document important test cases and coverage gaps.

22. Observability
    - Document logging, metrics, tracing, monitoring, alerts, and health checks.
    - Explain what should be monitored in production.
    - Identify important operational metrics and failure signals.

23. Design Decisions & Trade-offs
    - Document important architectural decisions.
    - Explain alternatives considered.
    - Explain advantages, disadvantages, constraints, and trade-offs.
    - Prefer evidence from the actual project over generic assumptions.

24. Security, Privacy & Compliance Considerations
    - Identify privacy-sensitive data and security boundaries.
    - Document data retention, access control, logging, and third-party data handling where applicable.
    - Mention relevant compliance considerations only when they actually apply.

25. Limitations & Known Issues
    - Clearly document current limitations.
    - Identify known bugs, unsupported scenarios, scalability limitations, model limitations, and technical debt.
    - Never hide limitations to make the project appear stronger.

26. Roadmap
    - Create a realistic future roadmap based on the project's current state.
    - Separate completed, in-progress, planned, and potential improvements.
    - Prioritize improvements by technical or product impact when evidence supports it.

27. Visual Documentation
    - Use Mermaid diagrams whenever appropriate.
    - Generate architecture diagrams, ER diagrams, sequence diagrams, flowcharts, deployment diagrams, component diagrams, and state diagrams when they improve understanding.
    - Every diagram must have a clear purpose and readable labels.
    - Do not create decorative diagrams that add no information.

28. Sequence & Workflow Diagrams
    - Use sequence diagrams to explain important interactions.
    - Show users, services, APIs, databases, queues, AI models, and external systems where relevant.
    - Document both normal flows and important failure flows.

29. Technical Glossary
    - Define project-specific terminology, acronyms, technologies, and domain concepts.
    - Keep definitions concise and understandable.
    - Avoid assuming that readers already understand internal terminology.

30. Professional README Generation
    - When asked to create a README, produce a complete production-quality README.
    - Include an appropriate structure such as:
      Overview, Problem, Solution, Features, Architecture, Tech Stack, Project Structure, Installation,
      Configuration, Usage, API, Database, AI/ML Pipeline, Testing, Deployment, Security, Limitations, Roadmap,
      Contributing, License
    - Only include sections relevant to the actual project.

31. Evidence-Based Documentation
    - Inspect the actual source code, configuration, dependency files, database schemas, API definitions, and deployment files before making technical claims.
    - Never invent functionality that does not exist.
    - Clearly mark assumptions when implementation details cannot be verified.

32. Documentation Consistency
    - Ensure terminology, component names, API names, folder names, database entities, and architecture diagrams are consistent throughout the documentation.
    - Do not describe the same component differently in different sections.

33. Audience Adaptation
    - Adapt documentation depth to the intended audience.
    - Developer documentation should be technically precise.
    - Product documentation should emphasize workflows and value.
    - Executive documentation should emphasize business impact, architecture at a high level, risks, and strategic considerations.

34. Documentation Quality Check
    - Before finalizing documentation, verify: technical accuracy, completeness, internal consistency, diagram
      correctness, code/example correctness, links, commands, API details, environment variables, formatting,
      spelling and grammar.
    - Remove unsupported claims and redundant sections.

35. Professional Presentation
    - Make documentation visually structured and easy to scan.
    - Use tables when comparisons are easier to understand in tabular form.
    - Use callouts for warnings, important notes, security considerations, and breaking changes.
    - Use code blocks for commands and configuration.
    - Keep paragraphs concise.

36. Project Comparison Matrix
    - When competitors exist, create a structured comparison matrix.
    - Compare only meaningful dimensions.
    - Separate verified capabilities from inferred differences.
    - Explain the project's differentiation without unsupported superiority claims.

37. Decision Documentation
    - For important engineering choices, document: Context, Problem, Options, Decision, Rationale, Trade-offs, Consequences.
    - Use ADR-style documentation when appropriate.

38. Maintainability
    - Write documentation that another developer can maintain after the original author leaves.
    - Avoid undocumented tribal knowledge.
    - Explain non-obvious implementation decisions.
    - Identify documentation that should be updated when specific code changes.

39. Documentation Automation
    - Where possible, derive documentation from source code, schemas, API specifications, configuration files, and repository metadata.
    - Prefer automatically verifiable information over manually assumed information.
    - Structure documentation so it can be regenerated or updated easily.

40. Final Documentation Standard
    - The final result should make a new developer understand:
      1. What the project is.
      2. What problem it solves.
      3. Who should use it.
      4. Why it exists.
      5. How it works.
      6. How the architecture is designed.
      7. How the data flows.
      8. How to install and run it.
      9. How to deploy it.
      10. How it compares with alternatives.
      11. What its limitations are.
      12. How it can be extended.
