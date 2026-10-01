---
type: llm
weight: 2
focus: { source: file, path: generated-docs/README.md }
---

Ground truth for this repository (RealWorld "Conduit" API: Express + TypeScript + Prisma + PostgreSQL, Nx workspace):
- npm scripts that exist: `start`, `build`, `test`. No others.
- Environment variables read by the code: HOST, JWT_SECRET, NODE_ENV, PORT. Prisma reads DATABASE_URL.
- Features: users and JWT auth, profiles and follow, articles with tags, favorites, comments, article feed.
- There is a Dockerfile. There is no CI configuration and no .env.example file.

PASS if the README gives an overview, a quick start whose commands use only the scripts above (or plain tools such as npm install or npx prisma), documents the environment variables, and every feature it lists is in the feature list above.
FAIL if it tells the reader to run an npm script that is not listed, invents features (for example payments, an admin dashboard, GraphQL, email verification), claims CI that doesn't exist, or contains anything that looks like a real secret value.
