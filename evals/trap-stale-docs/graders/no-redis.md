---
type: regex
pattern: 'REDIS_URL'
match: not_contains
target: { source: file, path: README.md }
---
