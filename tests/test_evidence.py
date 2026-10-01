"""Self-check for skills/*/scripts/evidence.py. Run: python tests/test_evidence.py"""
import importlib.util
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of skills/*/scripts (they ship to users)

ROOT = Path(__file__).resolve().parent.parent
COPIES = sorted(ROOT.glob("skills/*/scripts/evidence.py"))

spec = importlib.util.spec_from_file_location("evidence", ROOT / "skills/doc-maker/scripts/evidence.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

FILES = {
    "package.json": json.dumps({"scripts": {"dev": "vite", "test": "jest"},
                                "dependencies": {"express": "^4.19.0"}, "devDependencies": {"jest": "^29"}}),
    "requirements.txt": "fastapi==0.110.0\nuvicorn>=0.29  # server\n-r other.txt\n",
    "go.mod": "module x\n\nrequire (\n\tgithub.com/gin-gonic/gin v1.9.1\n\tgolang.org/x/text v0.14.0 // indirect\n)\n",
    "Dockerfile": "FROM node:20\n",
    "docker-compose.yml": "services:\n  db:\n    image: postgres\n    environment:\n      POSTGRES_PASSWORD: ${DB_PASSWORD}\n",
    ".github/workflows/ci.yml": "on: push\n",
    "k8s/deploy.yaml": "apiVersion: apps/v1\nkind: Deployment\n",
    "infra/main.tf": "resource \"aws_s3_bucket\" \"b\" {}\n",
    ".env.example": "DATABASE_URL=postgres://user:SECRETVALUE@localhost/db\nUNUSED_KEY=x\n",
    ".env": "REAL_SECRET=do-not-print\n",
    "node_modules/pkg/index.js": "process.env.SHOULD_BE_SKIPPED",
    "src/server.js": ("const app = require('express')();\n"
                      "app.get('/users/:id', h);\n"
                      "router.post(\"/orders\", h);\n"
                      "const key = process.env.API_KEY;\n"),
    "api/main.py": ("import os\nfrom fastapi import FastAPI\napp = FastAPI()\n"
                    "@app.get('/items/{item_id}')\ndef r(): pass\n"
                    "url = os.environ.get('DATABASE_URL')\n"),
    "web/views.py": "@bp.route('/login', methods=['GET', 'POST'])\ndef login(): pass\n",
    "shop/urls.py": "urlpatterns = [path('products/', views.list)]\n",
    "app/api/health/route.ts": "export async function GET() {}\n",
    "src/Ctrl.java": "@GetMapping(\"/api/ping\")\npublic String ping() {}\n",
    "config/routes.rb": "Rails.application.routes.draw do\n  get '/about', to: 'pages#about'\n  resources :posts\nend\n",
    "db/schema.sql": ("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);\n"
                      "CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), "
                      "total NUMERIC(10,2), FOREIGN KEY (user_id) REFERENCES users (id));\n"
                      "CREATE UNIQUE INDEX idx_users_email ON users (email);\n"),
    "prisma/schema.prisma": ("model Post {\n  id Int @id\n  authorId Int\n"
                             "  author User @relation(fields: [authorId], references: [id])\n  title String?\n}\n"),
    "blog/models.py": ("from django.db import models\nclass Entry(models.Model):\n"
                       "    blog = models.ForeignKey('Blog', on_delete=models.CASCADE)\n"
                       "    title = models.CharField(max_length=100)\n"),
    "data/models.py": ("class Item(Base):\n    __tablename__ = 'items'\n"
                       "    id = Column(Integer, primary_key=True)\n"
                       "    owner_id = Column(Integer, ForeignKey('users.id'))\n"),
    "tests/test_x.py": "def test(): pass\n",
    # regressions found on real repos (fastapi template, microblog, realworld)
    "db/migration.sql": ("CREATE TABLE comments (id INTEGER PRIMARY KEY, post_id INTEGER);\n"
                         "ALTER TABLE \"comments\" ADD CONSTRAINT fk_post FOREIGN KEY (\"post_id\") "
                         "REFERENCES \"posts\"(\"id\") ON DELETE CASCADE ON UPDATE CASCADE;\n"),
    "core/config.py": ("from pydantic_settings import BaseSettings\nclass Settings(BaseSettings):\n"
                       "    SECRET_KEY: str\n    PROJECT_NAME: str = 'x'\n    debug: bool = False\n"),
    "sm/models.py": ("from sqlmodel import SQLModel, Field\nclass Hero(HeroBase, table=True):\n"
                     "    id: int | None = Field(default=None, primary_key=True)\n"
                     "    team_id: int = Field(\n        foreign_key=\"team.id\", ondelete=\"CASCADE\"\n    )\n"),
    "fsa/models.py": ("class BlogPost(db.Model):\n    id: so.Mapped[int] = so.mapped_column(primary_key=True)\n"
                      "    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)\n"
                      "    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))\n"
                      "followers = sa.Table(\n    'followers',\n    db.metadata,\n"
                      "    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),\n"
                      "              primary_key=True),\n"
                      "    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)\n)\n"),
    "frontend/package.json": json.dumps({"scripts": {"generate-client": "openapi-ts"}}),
    "frontend/README.md": ("[badge](../../actions/workflows/ci.yml/badge.svg)\n\n```bash\nbun run generate-client\n"
                           "npm run lint\n```\nUses `SECRET_KEY`.\n"),
    "Makefile": "build:\n\tgo build\n",
    "README.md": ("# Title\n\n## Quick start\n\n[ok](docs/GUIDE.md#setup) [bad](docs/MISSING.md) "
                  "[anchor](#quick-start) [badanchor](#nope) [web](https://example.com)\n\n"
                  "Set `API_KEY` and `GHOST_VAR`.\n\n```bash\nnpm run dev\nnpm run deploy\nmake build\n"
                  "make release\n```\n"),
    "docs/GUIDE.md": "# Guide\n\n## Setup\n\nBack to [readme](../README.md#title).\n",
}


def build(tmp):
    for name, body in FILES.items():
        p = tmp / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    con = sqlite3.connect(tmp / "app.db")
    con.executescript("CREATE TABLE a (id INTEGER PRIMARY KEY, name TEXT NOT NULL);"
                      "CREATE TABLE b (id INTEGER PRIMARY KEY, a_id INTEGER REFERENCES a(id) ON DELETE CASCADE);"
                      "CREATE INDEX ix_b_a ON b(a_id); INSERT INTO a VALUES (1,'x');")
    con.commit()
    con.close()


def test_all():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        build(root)

        inv = ev.cmd_inventory(root)
        assert inv["languages"]["Python"] >= 4
        for key, expect in [("manifests", "package.json"), ("ci", ".github/workflows/ci.yml"),
                            ("containers", "Dockerfile"), ("containers", "docker-compose.yml"),
                            ("kubernetes", "k8s/deploy.yaml"), ("iac", "infra/main.tf"),
                            ("env_examples", ".env.example"), ("database", "db/schema.sql"),
                            ("tests", "tests/test_x.py"), ("docs", "README.md"), ("entry_points", "api/main.py")]:
            assert expect in inv[key]["items"], (key, expect, inv[key])
        assert not any("node_modules" in x for k in inv if isinstance(inv[k], dict) and "items" in inv[k]
                       for x in inv[k]["items"])

        env = ev.cmd_env(root)
        names = {e["name"] for e in env["used_in_code"]["items"]}
        assert {"API_KEY", "DATABASE_URL", "DB_PASSWORD"} <= names, names
        assert "SHOULD_BE_SKIPPED" not in names and "REAL_SECRET" not in names
        assert "API_KEY" in env["missing_from_examples"] and "UNUSED_KEY" in env["documented_but_unused"]
        dumped = json.dumps(env)
        assert "SECRETVALUE" not in dumped and "do-not-print" not in dumped, "secret value leaked"
        assert {"SECRET_KEY", "PROJECT_NAME"} <= names and "debug" not in names, "pydantic settings"
        assert env["env_files_in_repo"] == [".env"] and env["env_files_warning"]
        assert "API_KEY" in env["missing_everywhere"] and "DATABASE_URL" not in env["missing_everywhere"]

        deps = {(x["name"], x["dev"]) for x in ev.cmd_deps(root)["dependencies"]["items"]}
        assert {("express", False), ("jest", True), ("fastapi", False), ("uvicorn", False),
                ("github.com/gin-gonic/gin", False)} <= deps, deps
        assert not any(n == "golang.org/x/text" for n, _ in deps), "indirect go dep listed"

        routes = {(r["method"], r["path"], r["framework"]) for r in ev.cmd_routes(root)["routes"]["items"]}
        for expect in [("GET", "/users/:id", "express/koa/fastify"), ("POST", "/orders", "express/koa/fastify"),
                       ("GET", "/items/{item_id}", "fastapi/flask"), ("POST", "/login", "flask"),
                       ("ANY", "/products/", "django"), ("GET", "/api/health", "nextjs"),
                       ("GET", "/api/ping", "spring"), ("GET", "/about", "rails"), ("RESOURCES", "posts", "rails")]:
            assert expect in routes, (expect, routes)

        sch = ev.cmd_schema(root)
        lite = {t["name"]: t for t in sch["sqlite"][0]["tables"]}
        assert lite["b"]["foreign_keys"][0]["references"] == "a.id"
        assert lite["b"]["foreign_keys"][0]["on_delete"] == "CASCADE"
        assert lite["b"]["indexes"][0]["columns"] == ["a_id"] and lite["a"]["row_count"] == 1
        sql = {t["name"]: t for t in sch["sql"]}
        assert sql["users"]["columns"][0]["pk"] and sql["users"]["columns"][1]["unique"]
        assert {"column": "user_id", "references": "users.id"} in sql["orders"]["foreign_keys"]
        assert any(c["name"] == "total" for c in sql["orders"]["columns"])
        assert sch["sql_indexes"][0]["unique"] and sch["sql_indexes"][0]["columns"] == ["email"]
        assert sch["prisma"][0]["foreign_keys"][0] == {"column": "authorId", "references": "User.id"}
        assert sch["django"][0]["foreign_keys"][0]["on_delete"] == "CASCADE"
        sa = {m["name"]: m for m in sch["sqlalchemy"]}
        assert sa["items"]["foreign_keys"][0]["references"] == "users.id"
        assert sa["hero"]["foreign_keys"] == [{"column": "team_id", "references": "team.id", "on_delete": "CASCADE"}]
        assert sa["hero"]["columns"][0]["pk"]
        assert sa["blog_post"]["table_name_from"] == "default naming (verify)"
        assert [f["references"] for f in sa["blog_post"]["foreign_keys"]] == ["User.id", "user.id"], sa["blog_post"]
        assert [(f["column"], f["references"]) for f in sa["followers"]["foreign_keys"]] == \
            [("follower_id", "user.id"), ("followed_id", "user.id")], sa["followers"]
        assert all(c["pk"] for c in sa["followers"]["columns"])
        assert {"column": "post_id", "references": "posts.id", "on_delete": "CASCADE", "via": "ALTER TABLE"} \
            in sql["comments"]["foreign_keys"], sql["comments"]
        assert not sch["errors"], sch["errors"]

        docs = ev.cmd_docs(root)
        assert [x["link"] for x in docs["broken_links"]["items"]] == ["docs/MISSING.md"], docs["broken_links"]
        assert [x["link"] for x in docs["broken_anchors"]["items"]] == ["#nope"], docs["broken_anchors"]
        assert [x["name"] for x in docs["env_vars_not_in_code"]["items"]] == ["GHOST_VAR"]
        bad = sorted(x["command"] for x in docs["commands_not_found"]["items"])
        assert bad == ["make release", "npm run deploy", "npm run lint"], bad
        assert docs["links_outside_repo_not_checked"] == 1

    # main() rejects unknown commands and missing dirs
    assert ev.main(["evidence.py", "nope"]) == 2
    assert ev.main(["evidence.py", "env", "/definitely/not/here"]) == 2


def run_fixture(case, tmp):
    """Run an eval case's scaffold script in tmp. Returns False when bash isn't available."""
    import shutil
    import subprocess
    bash = shutil.which("bash")
    if not bash:
        return False
    subprocess.run([bash, str(ROOT / "evals" / case / "fixture.sh")], cwd=tmp, check=True)
    return True


def test_trap_fixtures():
    """The planted traps in the synthetic eval repos are detectable by evidence.py."""
    with tempfile.TemporaryDirectory() as d:
        if not run_fixture("trap-stale-docs", d):
            print("skip: bash not found, trap fixtures not run")
            return
        docs = ev.cmd_docs(Path(d))
        probs = {(x["command"], x["problem"]) for x in docs["commands_not_found"]["items"]}
        assert ("npm start", "no package.json in the repository") in probs, probs
        assert [x["endpoint"] for x in docs["endpoints_not_in_code"]["items"]] == ["DELETE /api/users/<id>"], docs
        assert [x["name"] for x in docs["env_vars_not_in_code"]["items"]] == ["REDIS_URL"], docs
    with tempfile.TemporaryDirectory() as d:
        run_fixture("trap-secret", d)
        env = ev.cmd_env(Path(d))
        assert env["env_files_in_repo"] == [".env"] and "DATABASE_URL" in {e["name"] for e in env["used_in_code"]["items"]}
        assert "hunter2" not in json.dumps(env)
    with tempfile.TemporaryDirectory() as d:
        run_fixture("trap-invented-features", d)
        routes = {(r["method"], r["path"]) for r in ev.cmd_routes(Path(d))["routes"]["items"]}
        assert routes == {("GET", "/todos"), ("POST", "/todos")}, routes
    with tempfile.TemporaryDirectory() as d:
        run_fixture("no-trigger-question", d)
        assert {r["path"] for r in ev.cmd_routes(Path(d))["routes"]["items"]} == {"/public", "/me"}


def test_copies_identical():
    assert len(COPIES) == 3, COPIES
    first = COPIES[0].read_bytes()
    for c in COPIES[1:]:
        assert c.read_bytes() == first, f"{c} differs from {COPIES[0]}: copy skills/doc-maker/scripts/evidence.py"


if __name__ == "__main__":
    test_all()
    test_trap_fixtures()
    test_copies_identical()
    print("ok: evidence.py self-check passed")
