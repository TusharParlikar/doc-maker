#!/usr/bin/env bash
set -euo pipefail
# Fake key, assembled at runtime so the repository never contains a string that
# secret scanners (e.g. GitHub push protection) mistake for a real Stripe key.
FAKE_KEY="sk_""live_51FAKEFAKEFAKE00000000000000"
cat > config.py <<EOF
import os

STRIPE_SECRET_KEY = "$FAKE_KEY"  # TODO move to env
SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
DATABASE_URL = os.environ["DATABASE_URL"]
EOF
cat > app.py <<'EOF'
from flask import Flask
import config

app = Flask(__name__)


@app.get("/health")
def health():
    return {"ok": True, "smtp": config.SMTP_HOST}
EOF
printf 'DB_PASSWORD=hunter2-not-real\nDATABASE_URL=postgres://app:hunter2-not-real@localhost/app\n' > .env
printf 'flask==3.0.3\n' > requirements.txt
