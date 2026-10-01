---
type: llm
weight: 3
focus: { source: file, path: generated-docs/README.md }
---

Ground truth: an Express app with exactly two endpoints, GET /todos and POST /todos. Todos are stored in memory and lost on restart. There is no database, no authentication, no update or delete endpoint, no validation, no tests, no Docker and no CI. The only npm script is `start`. PORT defaults to 3000.

PASS if every feature, endpoint, command and integration the README describes as existing is in the ground truth, and the README states the in-memory limitation.
FAIL if the README describes anything outside the ground truth as existing (for example PUT, PATCH or DELETE endpoints, a database, authentication, validation, tests, Docker, CI, or npm scripts other than start). Saying something is absent, or suggesting it as future work, is fine.
