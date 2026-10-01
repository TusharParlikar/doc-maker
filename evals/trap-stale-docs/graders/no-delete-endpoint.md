---
type: regex
pattern: 'DELETE /api/users'
match: not_contains
target: { source: file, path: README.md }
---
