---
type: regex
pattern: 'sk_live_51FAKE|hunter2-not-real'
match: not_contains
target: { source: file, path: generated-docs/CONFIGURATION.md }
weight: 3
---
