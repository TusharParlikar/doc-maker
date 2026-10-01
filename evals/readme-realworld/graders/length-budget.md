---
type: regex
pattern: '(?:\S+\s+){2200}'
match: not_contains
target: { source: file, path: generated-docs/README.md }
---
README stays under ~2,200 words.
