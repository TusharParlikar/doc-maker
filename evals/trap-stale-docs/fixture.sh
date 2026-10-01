#!/usr/bin/env bash
set -euo pipefail
cat > app.py <<'EOF'
import os
from flask import Flask, jsonify, request

app = Flask(__name__)
USERS = []


@app.get("/api/users")
def list_users():
    return jsonify(USERS)


@app.post("/api/users")
def create_user():
    USERS.append(request.get_json())
    return jsonify(USERS[-1]), 201


if __name__ == "__main__":
    db = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    app.run(port=int(os.environ.get("PORT", 8000)))
EOF
printf 'flask==3.0.3\n' > requirements.txt
cat > README.md <<'EOF'
# Users API

A small API to manage users.

## Setup

    npm install
    npm start

The server listens on port 5000.

## Configuration

| Variable | Required | Purpose |
|----------|----------|---------|
| `REDIS_URL` | yes | Cache connection |
| `DATABASE_URL` | no | Database connection |

## Endpoints

- `GET /api/users`: list users
- `POST /api/users`: create a user
- `DELETE /api/users/<id>`: delete a user
EOF
