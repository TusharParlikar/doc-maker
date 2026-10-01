#!/usr/bin/env python3
"""Read-only evidence collector for the Doc Maker skills.

Usage: python evidence.py <command> [repo_path]

Commands:
  inventory  languages, manifests, entry points, CI/container/IaC/platform files, docs, tests
  env        environment variables read in code vs keys listed in .env.example-style files
  deps       direct dependencies from common manifests
  routes     HTTP routes found by framework heuristics (verify before documenting)
  schema     tables, columns, keys and indexes from SQLite files, SQL, Prisma, Django, SQLAlchemy
  docs       broken links/anchors, unknown env vars, missing npm scripts / make targets in Markdown

Prints JSON. Never writes files, never prints secret values (only key names), opens SQLite read-only.
Standard library only; Python 3.8+ (pyproject parsing needs 3.11+).
"""
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "env", "__pycache__", "dist", "build", "target",
             "vendor", ".next", ".nuxt", "coverage", ".tox", ".mypy_cache", ".pytest_cache", ".idea",
             ".vscode", ".terraform", "site-packages", "bower_components", ".gradle", "out"}
MAX_BYTES = 1_000_000
LIMIT = 300  # max items per list in output; "truncated" is reported when hit

LANGS = {".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".jsx": "JavaScript",
         ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
         ".rb": "Ruby", ".php": "PHP", ".cs": "C#", ".swift": "Swift", ".scala": "Scala", ".c": "C", ".h": "C",
         ".cpp": "C++", ".hpp": "C++", ".dart": "Dart", ".ex": "Elixir", ".exs": "Elixir", ".sql": "SQL",
         ".tf": "Terraform", ".sh": "Shell", ".vue": "Vue", ".svelte": "Svelte", ".ipynb": "Jupyter"}
CODE_EXT = {e for e in LANGS if e not in {".sql", ".tf", ".ipynb"}}
MANIFESTS = {"package.json", "requirements.txt", "pyproject.toml", "Pipfile", "setup.py", "setup.cfg", "go.mod",
             "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile", "composer.json",
             "mix.exs", "pubspec.yaml", "Package.swift"}
ENTRY_NAMES = {"main.py", "app.py", "manage.py", "wsgi.py", "asgi.py", "server.py", "index.js", "server.js",
               "app.js", "main.js", "index.ts", "server.ts", "app.ts", "main.ts", "main.go", "main.rs",
               "Program.cs", "Application.java", "config.ru"}
PLATFORM = {"vercel.json", "netlify.toml", "render.yaml", "fly.toml", "Procfile", "app.json", "app.yaml",
            "railway.json", "railway.toml", "serverless.yml", "serverless.yaml", "firebase.json",
            "wrangler.toml", "amplify.yml", "heroku.yml", "skaffold.yaml", "Chart.yaml"}
CI_FILES = {".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml", "bitbucket-pipelines.yml", ".travis.yml",
            "cloudbuild.yaml", "buildspec.yml"}
ENV_EXAMPLES = {".env.example", ".env.sample", ".env.template", ".env.dist", "example.env", "sample.env",
                ".env.defaults", "env.example"}


def walk(root):
    """Yield files under root, skipping vendored/build dirs and big files."""
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.endswith(".egg-info"))
        for f in sorted(files):
            p = Path(d) / f
            try:
                if p.stat().st_size <= MAX_BYTES:
                    yield p
            except OSError:
                continue


def read(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def rel(p, root):
    return p.relative_to(root).as_posix()


def cap(items):
    return {"count": len(items), "items": items[:LIMIT], "truncated": len(items) > LIMIT}


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


# ---------------------------------------------------------------- inventory
def cmd_inventory(root):
    langs, out = {}, {k: [] for k in ("manifests", "entry_points", "ci", "containers", "kubernetes", "iac",
                                      "platform", "docs", "env_examples", "database", "tests")}
    for p in walk(root):
        r, name, ext = rel(p, root), p.name, p.suffix.lower()
        if ext in LANGS:
            langs[LANGS[ext]] = langs.get(LANGS[ext], 0) + 1
        parts = r.split("/")
        if name in MANIFESTS or name.endswith(".csproj") or (name.startswith("requirements") and ext == ".txt"):
            out["manifests"].append(r)
        if name in ENTRY_NAMES or re.fullmatch(r"cmd/[^/]+/main\.go", r):
            out["entry_points"].append(r)
        if name in CI_FILES or r.startswith((".github/workflows/", ".circleci/")):
            out["ci"].append(r)
        if name.startswith("Dockerfile") or name.endswith(".dockerfile") or re.fullmatch(
                r"(docker-)?compose(\.[\w-]+)?\.ya?ml", name):
            out["containers"].append(r)
        if ext in (".yaml", ".yml"):
            head = read(p)[:4000]
            if re.search(r"^apiVersion:", head, re.M) and re.search(r"^kind:", head, re.M):
                out["kubernetes"].append(r)
            if "AWSTemplateFormatVersion" in head or "Transform: AWS::Serverless" in head:
                out["iac"].append(r)
        if ext in (".tf", ".bicep") or name in ("Pulumi.yaml", "cdk.json", "terragrunt.hcl"):
            out["iac"].append(r)
        if name in PLATFORM:
            out["platform"].append(r)
        if ext in (".md", ".mdx", ".rst") and (len(parts) == 1 or parts[0] in ("docs", "doc", "documentation")):
            out["docs"].append(r)
        if name in ENV_EXAMPLES:
            out["env_examples"].append(r)
        if (ext in (".sql", ".sqlite", ".sqlite3", ".db") or name == "schema.prisma"
                or any(x in ("migrations", "migrate", "alembic") for x in parts[:-1])):
            out["database"].append(r)
        if (any(x in ("test", "tests", "__tests__", "spec", "specs") for x in parts[:-1])
                or re.match(r"(tests?\.py|test_.+\.py|.+_test\.(py|go)|.+\.(test|spec)\.[jt]sx?)$", name)):
            out["tests"].append(r)
    result = {"root": str(root), "languages": dict(sorted(langs.items(), key=lambda x: -x[1]))}
    result.update({k: cap(v) for k, v in out.items()})
    return result


# ---------------------------------------------------------------- env
ENV_PATTERNS = [
    r"os\.environ\[\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"os\.environ\.get\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"os\.getenv\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"process\.env\.([A-Z][A-Z0-9_]+)",
    r"process\.env\[\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"import\.meta\.env\.([A-Z][A-Z0-9_]+)",
    r"os\.(?:Getenv|LookupEnv)\(\s*\"([A-Z][A-Z0-9_]+)\"",
    r"ENV(?:\.fetch\(\s*|\[\s*)['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"System\.getenv\(\s*\"([A-Z][A-Z0-9_]+)\"",
    r"env::var\(\s*\"([A-Z][A-Z0-9_]+)\"",
    r"getenv\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"\$_(?:ENV|SERVER)\[\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"Environment\.GetEnvironmentVariable\(\s*\"([A-Z][A-Z0-9_]+)\"",
]
ENV_RE = re.compile("|".join(ENV_PATTERNS))
COMPOSE_VAR_RE = re.compile(r"\$\{([A-Z][A-Z0-9_]+)(?::?-[^}]*)?\}")


def env_used(root):
    used = {}
    for p in walk(root):
        is_compose = re.fullmatch(r"(docker-)?compose(\.[\w-]+)?\.ya?ml", p.name)
        if p.suffix.lower() not in CODE_EXT and not is_compose:
            continue
        text = read(p)
        for m in (COMPOSE_VAR_RE if is_compose else ENV_RE).finditer(text):
            name = next(g for g in m.groups() if g)
            used.setdefault(name, []).append(f"{rel(p, root)}:{lineno(text, m.start())}")
        if p.suffix == ".py" and "BaseSettings" in text:  # pydantic settings: UPPER_CASE fields come from env
            for c in re.finditer(r"^class\s+\w+\([^)]*BaseSettings[^)]*\):(.*?)(?=^\S|\Z)", text, re.M | re.S):
                for f in re.finditer(r"^\s+([A-Z][A-Z0-9_]+)\s*:", c.group(1), re.M):
                    used.setdefault(f.group(1), []).append(
                        f"{rel(p, root)}:{lineno(text, c.start(1) + f.start())} (pydantic settings)")
    return used


def is_env_file(name):
    return name == ".env" or (name.startswith(".env.") and name not in ENV_EXAMPLES)


def env_keys(root, files_match):
    """Key names from dotenv-style files. Values are never kept or printed."""
    keys = {}
    for p in walk(root):
        if files_match(p.name):
            for line in read(p).splitlines():
                m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
                if m:
                    keys.setdefault(m.group(1), rel(p, root))
    return keys


def env_documented(root):
    return env_keys(root, lambda n: n in ENV_EXAMPLES)


def cmd_env(root):
    used, documented = env_used(root), env_documented(root)
    env_files = env_keys(root, is_env_file)
    known = set(documented) | set(env_files)
    return {
        "note": "Key names only; values are never printed.",
        "used_in_code": cap([{"name": k, "locations": v[:10]} for k, v in sorted(used.items())]),
        "documented_in_examples": sorted(documented),
        "env_files_in_repo": sorted(set(env_files.values())),
        "env_files_warning": ("Real .env files are present in the repository. Check whether they are committed "
                              "and whether they hold real secrets." if env_files else None),
        "missing_from_examples": sorted(set(used) - set(documented)),
        "missing_everywhere": sorted(set(used) - known),
        "documented_but_unused": sorted(set(documented) - set(used)),
    }


# ---------------------------------------------------------------- deps
def _req_lines(text):
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if line and not line.startswith(("-", "git+", "http")):
            m = re.match(r"([A-Za-z0-9_.\-\[\]]+)\s*(.*)", line)
            if m:
                yield m.group(1), m.group(2).strip() or "*"


def cmd_deps(root):
    deps = []

    def add(name, spec, dev, src):
        deps.append({"name": name, "version": spec, "dev": dev, "file": src})

    for p in walk(root):
        name, r, text = p.name, rel(p, root), None
        if name == "package.json":
            try:
                data = json.loads(read(p))
            except ValueError:
                continue
            for sec, dev in (("dependencies", False), ("devDependencies", True), ("peerDependencies", False)):
                for k, v in (data.get(sec) or {}).items():
                    add(k, v, dev, r)
        elif name.startswith("requirements") and name.endswith(".txt"):
            for k, v in _req_lines(read(p)):
                add(k, v, "dev" in name, r)
        elif name == "pyproject.toml":
            try:
                import tomllib
                data = tomllib.loads(read(p))
            except Exception:
                continue
            for s in data.get("project", {}).get("dependencies", []):
                m = re.match(r"([A-Za-z0-9_.\-\[\]]+)\s*(.*)", s)
                if m:
                    add(m.group(1), m.group(2) or "*", False, r)
            for grp, items in data.get("project", {}).get("optional-dependencies", {}).items():
                for s in items:
                    m = re.match(r"([A-Za-z0-9_.\-\[\]]+)\s*(.*)", s)
                    if m:
                        add(m.group(1), m.group(2) or "*", grp in ("dev", "test", "lint"), r)
            for k, v in data.get("tool", {}).get("poetry", {}).get("dependencies", {}).items():
                if k != "python":
                    add(k, v if isinstance(v, str) else json.dumps(v), False, r)
        elif name == "go.mod":
            text = read(p)
            for m in re.finditer(r"^\s*(?:require\s+)?([\w.\-]+\.[\w.\-/]+)\s+(v[\w.\-+]+)(\s*//\s*indirect)?",
                                 text, re.M):
                if not m.group(3):
                    add(m.group(1), m.group(2), False, r)
        elif name == "Cargo.toml":
            sec = None
            for line in read(p).splitlines():
                h = re.match(r"\s*\[([^\]]+)\]", line)
                if h:
                    sec = h.group(1)
                    continue
                if sec in ("dependencies", "dev-dependencies", "build-dependencies"):
                    m = re.match(r"\s*([A-Za-z0-9_\-]+)\s*=\s*(.+)", line)
                    if m:
                        add(m.group(1), m.group(2).strip(), sec != "dependencies", r)
        elif name == "pom.xml":
            for m in re.finditer(r"<dependency>(.*?)</dependency>", read(p), re.S):
                block = m.group(1)
                g = re.search(r"<groupId>(.*?)</groupId>", block)
                a = re.search(r"<artifactId>(.*?)</artifactId>", block)
                v = re.search(r"<version>(.*?)</version>", block)
                sc = re.search(r"<scope>(.*?)</scope>", block)
                if a:
                    add(f"{g.group(1) + ':' if g else ''}{a.group(1)}", v.group(1) if v else "*",
                        bool(sc and sc.group(1) == "test"), r)
        elif name == "Gemfile":
            for m in re.finditer(r"^\s*gem\s+['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?", read(p), re.M):
                add(m.group(1), m.group(2) or "*", False, r)
        elif name == "composer.json":
            try:
                data = json.loads(read(p))
            except ValueError:
                continue
            for sec, dev in (("require", False), ("require-dev", True)):
                for k, v in (data.get(sec) or {}).items():
                    add(k, v, dev, r)
    return {"dependencies": cap(deps),
            "note": "Direct dependencies only. Lockfiles hold resolved versions."}


# ---------------------------------------------------------------- routes
METHODS = "get|post|put|patch|delete|options|head|all"
ROUTE_RULES = [
    ("express/koa/fastify", (".js", ".mjs", ".cjs", ".ts"),
     re.compile(rf"\b(?:app|router|server|api|fastify|route[rs]?)\.({METHODS})\(\s*['\"`]([^'\"`]+)['\"`]", re.I)),
    ("fastapi/flask", (".py",),
     re.compile(r"@\w+\.(get|post|put|patch|delete|options|head)\(\s*['\"]([^'\"]*)['\"]")),
    ("flask", (".py",), re.compile(r"@\w+\.route\(\s*['\"]([^'\"]*)['\"]([^)]*)\)")),
    ("django", (".py",), re.compile(r"\b(?:re_)?path\(\s*r?['\"]([^'\"]*)['\"]")),
    ("spring", (".java", ".kt"),
     re.compile(r"@(Get|Post|Put|Delete|Patch|Request)Mapping\(\s*(?:value\s*=\s*|path\s*=\s*)?\{?\s*\"([^\"]*)\"")),
    ("rails", (".rb",), re.compile(r"^\s*(get|post|put|patch|delete|resources?)\s+[:'\"]([\w/:\-]+)['\"]?", re.M)),
]


def cmd_routes(root):
    routes = []
    for p in walk(root):
        r, ext = rel(p, root), p.suffix.lower()
        # Next.js file-based routes
        m = re.match(r"(?:src/)?app/(.*)/route\.[jt]sx?$", r) or re.match(r"(?:src/)?pages/(api/.*)\.[jt]sx?$", r)
        if m:
            path = "/" + re.sub(r"\[([^\]]+)\]", r":\1", re.sub(r"/?index$", "", m.group(1)))
            path = re.sub(r"\(([^)]+)\)/", "", path)  # route groups
            text = read(p)
            methods = re.findall(r"export\s+(?:async\s+)?(?:function|const)\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b",
                                 text) or ["ANY"]
            for meth in methods:
                routes.append({"method": meth, "path": path, "framework": "nextjs", "location": r})
            continue
        for fw, exts, rx in ROUTE_RULES:
            if ext not in exts or (fw == "django" and p.name != "urls.py") or (
                    fw == "rails" and not r.endswith("config/routes.rb")):
                continue
            text = read(p)
            for m in rx.finditer(text):
                loc = f"{r}:{lineno(text, m.start())}"
                if fw == "flask":
                    ms = re.findall(r"['\"](GET|POST|PUT|PATCH|DELETE)['\"]", m.group(2), re.I) or ["GET"]
                    for meth in ms:
                        routes.append({"method": meth.upper(), "path": m.group(1), "framework": fw, "location": loc})
                elif fw == "django":
                    routes.append({"method": "ANY", "path": "/" + m.group(1), "framework": fw, "location": loc})
                elif fw == "spring":
                    meth = "ANY" if m.group(1) == "Request" else m.group(1).upper()
                    routes.append({"method": meth, "path": m.group(2), "framework": fw, "location": loc})
                else:
                    meth = m.group(1).upper()
                    routes.append({"method": "RESOURCES" if meth.startswith("RESOURCE") else meth,
                                   "path": m.group(2), "framework": fw, "location": loc})
    return {"routes": cap(routes),
            "note": "Regex heuristics: router prefixes, class-level mappings and dynamic routes are not "
                    "combined. Open each location to confirm the full path before documenting it."}


# ---------------------------------------------------------------- schema
def sqlite_schema(path):
    uri = "file:" + path.resolve().as_posix() + "?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        tables = []
        for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' "
                                   "AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            q = name.replace('"', '""')
            cols = [{"name": c[1], "type": c[2], "not_null": bool(c[3]), "default": c[4], "pk": bool(c[5])}
                    for c in con.execute(f'PRAGMA table_info("{q}")')]
            fks = [{"column": f[3], "references": f"{f[2]}.{f[4]}", "on_update": f[5], "on_delete": f[6]}
                   for f in con.execute(f'PRAGMA foreign_key_list("{q}")')]
            idx = []
            for i in con.execute(f'PRAGMA index_list("{q}")'):
                iq = i[1].replace('"', '""')
                idx.append({"name": i[1], "unique": bool(i[2]),
                            "columns": [c[2] for c in con.execute(f'PRAGMA index_info("{iq}")')]})
            rows = con.execute(f'SELECT COUNT(*) FROM "{q}"').fetchone()[0]
            tables.append({"name": name, "columns": cols, "foreign_keys": fks, "indexes": idx, "row_count": rows})
        return tables
    finally:
        con.close()


def _q(s):
    return s.strip(' `"')


def _split_top(body):
    parts, depth, cur = [], 0, ""
    for ch in body:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def sql_schema(text, src):
    tables, indexes = [], []
    for m in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"\[]?([\w.]+)[`\"\]]?\s*\((.*?)\)\s*;",
                         text, re.I | re.S):
        cols, fks, pks = [], [], []
        for part in _split_top(m.group(2)):
            up = part.upper()
            if up.startswith(("PRIMARY KEY", "CONSTRAINT", "FOREIGN KEY", "UNIQUE", "CHECK", "INDEX", "KEY ")):
                fk = re.search(r"FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+[`\"]?([\w.]+)[`\"]?\s*\(([^)]+)\)", part, re.I)
                if fk:
                    fks.append({"column": fk.group(1).strip(' `"'), "references": fk.group(2) + "." + _q(fk.group(3))})
                pk = re.search(r"PRIMARY\s+KEY\s*\(([^)]+)\)", part, re.I)
                if pk:
                    pks += [c.strip(' `"') for c in pk.group(1).split(",")]
                continue
            cm = re.match(r"[`\"\[]?(\w+)[`\"\]]?\s+([\w]+(?:\s*\([^)]*\))?)(.*)", part, re.S)
            if not cm:
                continue
            rest = cm.group(3)
            ref = re.search(r"REFERENCES\s+[`\"]?([\w.]+)[`\"]?\s*\(([^)]+)\)", rest, re.I)
            if ref:
                fks.append({"column": cm.group(1), "references": ref.group(1) + "." + _q(ref.group(2))})
            cols.append({"name": cm.group(1), "type": cm.group(2), "not_null": bool(re.search(r"NOT\s+NULL", rest, re.I)),
                         "pk": bool(re.search(r"PRIMARY\s+KEY", rest, re.I)), "unique": bool(re.search(r"\bUNIQUE\b", rest, re.I))})
        for c in cols:
            c["pk"] = c["pk"] or c["name"] in pks
        tables.append({"name": m.group(1), "columns": cols, "foreign_keys": fks, "source": src})
    alter = re.compile(r"ALTER\s+TABLE\s+(?:ONLY\s+)?[`\"]?([\w.]+)[`\"]?\s+ADD\s+(?:CONSTRAINT\s+[`\"]?\w+[`\"]?\s+)?"
                       r"FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+[`\"]?([\w.]+)[`\"]?\s*\(([^)]+)\)([^;]*)", re.I)
    by_name = {t["name"]: t for t in tables}
    for m in alter.finditer(text):
        ondel = re.search(r"ON\s+DELETE\s+(CASCADE|SET\s+NULL|SET\s+DEFAULT|RESTRICT|NO\s+ACTION)", m.group(5), re.I)
        fk = {"column": _q(m.group(2)), "references": m.group(3) + "." + _q(m.group(4)),
              "on_delete": ondel.group(1).upper() if ondel else None, "via": "ALTER TABLE"}
        if m.group(1) in by_name:
            by_name[m.group(1)]["foreign_keys"].append(fk)
        else:
            tables.append({"name": m.group(1), "columns": [], "foreign_keys": [fk], "source": src,
                           "note": "table created elsewhere"})
            by_name[m.group(1)] = tables[-1]
    for m in re.finditer(r"CREATE\s+(UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?(\w+)[`\"]?\s+ON\s+[`\"]?([\w.]+)[`\"]?\s*\(([^)]+)\)",
                         text, re.I):
        indexes.append({"name": m.group(2), "table": m.group(3), "unique": bool(m.group(1)),
                        "columns": [c.strip(' `"') for c in m.group(4).split(",")], "source": src})
    return tables, indexes


def prisma_schema(text, src):
    models = []
    for m in re.finditer(r"^model\s+(\w+)\s*\{(.*?)^\}", text, re.M | re.S):
        fields, fks = [], []
        for line in m.group(2).splitlines():
            f = re.match(r"\s*(\w+)\s+(\w+)(\[\])?(\?)?(.*)", line)
            if not f or line.strip().startswith(("//", "@@")):
                continue
            rest = f.group(5)
            rel_m = re.search(r"@relation\([^)]*fields:\s*\[([^\]]+)\][^)]*references:\s*\[([^\]]+)\]", rest)
            if rel_m:
                fks.append({"column": rel_m.group(1).strip(), "references": f"{f.group(2)}.{rel_m.group(2).strip()}"})
            fields.append({"name": f.group(1), "type": f.group(2) + (f.group(3) or ""), "nullable": bool(f.group(4)),
                           "pk": "@id" in rest, "unique": "@unique" in rest})
        models.append({"name": m.group(1), "columns": fields, "foreign_keys": fks, "source": src})
    return models


def django_models(text, src):
    models = []
    for m in re.finditer(r"^class\s+(\w+)\(([^)]*models\.Model[^)]*)\):(.*?)(?=^\S|\Z)", text, re.M | re.S):
        fields, fks = [], []
        for f in re.finditer(r"^\s+(\w+)\s*=\s*models\.(\w+)\(", m.group(3), re.M):
            args = _balanced(m.group(3), f.end())
            fields.append({"name": f.group(1), "type": f.group(2)})
            if f.group(2) in ("ForeignKey", "OneToOneField", "ManyToManyField"):
                target = re.match(r"\s*['\"]?([\w.]+)", args)
                ondel = re.search(r"on_delete\s*=\s*models\.(\w+)", args)
                fks.append({"column": f.group(1), "references": target.group(1) if target else "?",
                            "kind": f.group(2), "on_delete": ondel.group(1) if ondel else None})
        models.append({"name": m.group(1), "columns": fields, "foreign_keys": fks, "source": src})
    return models


def _balanced(text, start):
    """Text from start up to the ")" that closes an already-open "("."""
    depth = 1
    for i in range(start, min(len(text), start + 2000)):
        depth += (text[i] == "(") - (text[i] == ")")
        if depth == 0:
            return text[start:i]
    return text[start:start + 2000]


def _snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def sqlalchemy_models(text, src):
    """SQLAlchemy / Flask-SQLAlchemy (Column, mapped_column) and SQLModel (table=True, Field)."""
    models = []
    for m in re.finditer(r"^class\s+(\w+)\(([^)]*)\):(.*?)(?=^\S|\Z)", text, re.M | re.S):
        bases, body = m.group(2), m.group(3)
        t = re.search(r"__tablename__\s*=\s*['\"](\w+)['\"]", body)
        sqlmodel = "table=True" in bases
        orm_base = re.search(r"\b(db\.Model|Base|DeclarativeBase)\b", bases)
        if not (t or sqlmodel or (orm_base and re.search(r"(Column|mapped_column)\(", body))):
            continue
        fields, fks = [], []
        call = r"Field" if sqlmodel else r"(?:\w+\.)?(?:Column|mapped_column)"
        for f in re.finditer(rf"^\s+(\w+)\s*(?::\s*[^=\n]+)?=\s*{call}\(", body, re.M):
            args = _balanced(body, f.end())
            fields.append({"name": f.group(1), "pk": "primary_key=True" in args})
            fk = re.search(r"(?:ForeignKey\(\s*|foreign_key\s*=\s*)['\"]?([\w.]+)", args)
            if fk:
                od = re.search(r"ondelete\s*=\s*['\"](\w[\w ]*)['\"]", args)
                fks.append({"column": f.group(1), "references": fk.group(1), "on_delete": od.group(1) if od else None})
        name = t.group(1) if t else (m.group(1).lower() if sqlmodel else _snake(m.group(1)))
        models.append({"name": name, "class": m.group(1), "columns": fields, "foreign_keys": fks, "source": src,
                       "table_name_from": "__tablename__" if t else "default naming (verify)",
                       "note": "fields inherited from base classes are not listed" if "Base" in bases or sqlmodel else None})
    # SQLAlchemy Core tables, e.g. association tables: name = sa.Table('name', metadata, Column(...), ...)
    for m in re.finditer(r"^\w+\s*=\s*(?:\w+\.)?Table\(\s*['\"](\w+)['\"]", text, re.M):
        args = _balanced(text, text.index("(", m.start()) + 1)
        fields, fks = [], []
        for c in re.finditer(r"Column\(\s*['\"](\w+)['\"]", args):
            cargs = _balanced(args, c.end())
            fields.append({"name": c.group(1), "pk": "primary_key=True" in cargs})
            fk = re.search(r"ForeignKey\(\s*['\"]?([\w.]+)", cargs)
            if fk:
                fks.append({"column": c.group(1), "references": fk.group(1), "on_delete": None})
        models.append({"name": m.group(1), "class": None, "columns": fields, "foreign_keys": fks, "source": src,
                       "table_name_from": "Table()", "note": "SQLAlchemy Core table (often an association table)"})
    return models


def cmd_schema(root):
    out = {"sqlite": [], "sql": [], "sql_indexes": [], "prisma": [], "django": [], "sqlalchemy": [], "errors": []}
    for p in walk(root):
        r, ext = rel(p, root), p.suffix.lower()
        try:
            if ext in (".db", ".sqlite", ".sqlite3"):
                with open(p, "rb") as fh:
                    if fh.read(16) == b"SQLite format 3\x00":
                        out["sqlite"].append({"file": r, "tables": sqlite_schema(p)})
            elif ext == ".sql":
                t, i = sql_schema(read(p), r)
                out["sql"] += t
                out["sql_indexes"] += i
            elif p.name == "schema.prisma":
                out["prisma"] += prisma_schema(read(p), r)
            elif ext == ".py":
                text = read(p)
                if "models.Model" in text:
                    out["django"] += django_models(text, r)
                if re.search(r"__tablename__|table=True|mapped_column\(|db\.Model|\bTable\(\s*['\"]", text):
                    out["sqlalchemy"] += sqlalchemy_models(text, r)
        except (sqlite3.Error, OSError) as e:
            out["errors"].append(f"{r}: {e}")
    out["note"] = ("SQL files are parsed one by one; ALTER TABLE and migration order are not applied. "
                   "Compare sources and report differences instead of picking one (database-docs rule 60).")
    return out


# ---------------------------------------------------------------- docs
def gh_slug(heading):
    h = re.sub(r"<[^>]+>", "", heading).strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors_of(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    ids, seen = set(), {}
    for h in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        s = gh_slug(h)
        n = seen.get(s, 0)
        ids.add(s if n == 0 else f"{s}-{n}")
        seen[s] = n + 1
    ids.update(re.findall(r"<a\s+(?:id|name)=\"([^\"]+)\"", text))
    return ids


def cmd_docs(root):
    md = [p for p in walk(root) if p.suffix.lower() in (".md", ".mdx")]
    used_env = set(env_used(root)) | set(env_documented(root)) | set(env_keys(root, is_env_file))
    npm_scripts, make_targets, has_pkg, has_make = set(), set(), False, False
    for p in walk(root):  # scripts/targets from every package.json and Makefile (monorepos, sub-apps)
        if p.name == "package.json":
            has_pkg = True
            try:
                npm_scripts |= set((json.loads(read(p)).get("scripts") or {}))
            except ValueError:
                pass
        elif p.name in ("Makefile", "makefile", "GNUmakefile"):
            has_make = True
            make_targets |= set(re.findall(r"^([A-Za-z0-9_.\-]+)\s*:(?!=)", read(p), re.M))
    broken_links, broken_anchors, bad_cmds, outside = [], [], [], 0
    unknown_env, bad_endpoints = {}, []
    cache = {}
    norm = lambda path: re.sub(r"(\{[^}]*\}|<[^>]*>|:\w+|\[[^\]]+\])", "{}", path.rstrip("/") or "/")
    code_routes = cmd_routes(root)["routes"]["items"]
    known = {(r["method"], norm(r["path"])) for r in code_routes}
    known_paths = {norm(r["path"]) for r in code_routes}
    for p in md:
        text = read(p)
        prose = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
        for m in re.finditer(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)", prose):
            target = m.group(1)
            if re.match(r"[a-z][a-z0-9+.\-]*:", target, re.I) or target.startswith("//"):
                continue
            path_part, _, frag = target.partition("#")
            loc = f"{rel(p, root)}:{lineno(prose, m.start())}"
            dest = p if not path_part else (p.parent / path_part).resolve()
            if path_part and root not in dest.parents and dest != root:
                outside += 1  # e.g. ../../actions/... GitHub UI links: can't be checked from the repo
                continue
            if path_part and not dest.exists():
                broken_links.append({"link": target, "location": loc})
                continue
            if frag and dest.suffix.lower() in (".md", ".mdx") and dest.is_file():
                if dest not in cache:
                    cache[dest] = anchors_of(read(dest))
                if frag.lower() not in cache[dest]:
                    broken_anchors.append({"link": target, "location": loc})
        if code_routes:  # endpoints named in docs but not found in code (only when routes were detected)
            for m in re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(`?)(/[\w/{}<>:.\-\[\]]*)", text):
                raw = m.group(3).rstrip(".,;:])")
                if raw == "/" and not m.group(2):  # bare "DELETE /" is usually prose ("ON DELETE / ON UPDATE")
                    continue
                meth, path = m.group(1), norm(raw)
                if ((meth, path) not in known and ("ANY", path) not in known
                        and not any(path.endswith(k) and k != "/" for k in known_paths if (meth, k) in known)):
                    bad_endpoints.append({"endpoint": f"{meth} {raw}",
                                          "location": f"{rel(p, root)}:{lineno(text, m.start())}"})
        for m in re.finditer(r"`([A-Z][A-Z0-9]*_[A-Z0-9_]+)`", text):
            if m.group(1) not in used_env:
                unknown_env.setdefault(m.group(1), f"{rel(p, root)}:{lineno(text, m.start())}")
        shell_lines = []  # (line number, command) from fenced shell blocks and indented code blocks
        for block in re.finditer(r"```(?:bash|sh|shell|console|zsh|powershell|ps1)?\n(.*?)```", text, re.S):
            start = lineno(text, block.start())
            shell_lines += [(start + i, ln) for i, ln in enumerate(block.group(1).splitlines(), 1)]
        shell_lines += [(lineno(prose, m.start()), m.group(1)) for m in re.finditer(r"^(?: {4}|\t)(\S.*)$", prose, re.M)]
        for num, line in shell_lines:
            line = line.strip().lstrip("$ ").strip()
            where = f"{rel(p, root)}:{num}"
            if re.match(r"(npm|yarn|pnpm|bun|npx)\b", line) and not has_pkg:
                bad_cmds.append({"command": line, "problem": "no package.json in the repository", "location": where})
                continue
            n = re.match(r"(?:npm\s+run|npm(?=\s+(?:start|test)\b)|yarn(?:\s+run)?|pnpm(?:\s+run)?|bun\s+run)"
                         r"\s+([\w:.\-]+)", line)
            if n and n.group(1) not in npm_scripts and n.group(1) not in (
                    "install", "add", "dlx", "create", "exec", "init", "i", "ci"):
                bad_cmds.append({"command": line, "problem": "no such package.json script", "location": where})
            k = re.match(r"make(?:\s+([\w.\-]+))?\s*$", line)
            if k and not has_make:
                bad_cmds.append({"command": line, "problem": "no Makefile in the repository", "location": where})
            elif k and k.group(1) and k.group(1) not in make_targets:
                bad_cmds.append({"command": line, "problem": "no such Makefile target", "location": where})
    return {"markdown_files": len(md), "broken_links": cap(broken_links), "broken_anchors": cap(broken_anchors),
            "env_vars_not_in_code": cap([{"name": k, "location": v} for k, v in sorted(unknown_env.items())]),
            "commands_not_found": cap(bad_cmds), "endpoints_not_in_code": cap(bad_endpoints),
            "links_outside_repo_not_checked": outside,
            "note": "External URLs are not fetched. Env var check covers `UPPER_SNAKE` names in backticks. "
                    "Scripts and make targets are collected from every package.json and Makefile in the repo."}


COMMANDS = {"inventory": cmd_inventory, "env": cmd_env, "deps": cmd_deps, "routes": cmd_routes,
            "schema": cmd_schema, "docs": cmd_docs}


def main(argv):
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(__doc__)
        return 2
    root = Path(argv[2] if len(argv) > 2 else ".").resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}))
        return 2
    print(json.dumps(COMMANDS[argv[1]](root), indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
