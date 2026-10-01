# README template

Use the sections that apply; delete the rest. Tier 1 sections are always written. Budget: about 1,200 words for a small project, 2,000 for a large one. Move anything longer into `docs/` and link to it.

```markdown
# <Project name>

<One sentence: what it is and who it is for.>

<2-4 sentences: the problem it solves and how, in plain words.>            <!-- Tier 1 -->

## Features                                                                  <!-- Tier 1, 3-8 bullets -->
- **<Feature>**: <what the user gets>. <!-- each feature must map to code you saw -->

## Quick start                                                               <!-- Tier 1 -->
Prerequisites: <runtime + version from manifests>, <services, e.g. PostgreSQL 15>.

    git clone <url>
    cd <dir>
    <install command from the lockfile's tool>
    cp .env.example .env        # then fill in the values listed under Configuration
    <run command that exists in package.json / Makefile / manage.py>

Open <URL or expected output>.

## Configuration                                                             <!-- Tier 1 if env vars exist -->
| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `<NAME>` | yes | – | <purpose>. Placeholder only, never a real value. |

## Architecture                                                              <!-- Tier 1: summary + one diagram -->
<3-5 sentences + one Mermaid diagram. Link docs/ARCHITECTURE.md for detail.>

## Usage / API                                                               <!-- Tier 2: when there is an interface -->
<Main commands or endpoints with one example each. Full reference in docs/.>

## Development                                                               <!-- Tier 2 -->
<Run tests, lint, format: only commands that exist.>

## Limitations                                                               <!-- Tier 1 -->
- <Known limitation, unsupported case, or tech debt, stated plainly.>

## Documentation                                                             <!-- when docs/ exists -->
- [Architecture](docs/ARCHITECTURE.md) · [Database](docs/DATABASE.md) · ...

## License
<From the LICENSE file; say "No license file" if there is none.>
```
