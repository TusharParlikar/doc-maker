#!/usr/bin/env bash
set -euo pipefail
mkdir -p middleware
cat > middleware/auth.js <<'EOF'
const jwt = require('jsonwebtoken');

module.exports = function requireAuth(req, res, next) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch (e) {
    res.status(401).json({ error: 'unauthorized' });
  }
};
EOF
cat > server.js <<'EOF'
const express = require('express');
const requireAuth = require('./middleware/auth');
const app = express();
app.get('/public', (req, res) => res.send('ok'));
app.get('/me', requireAuth, (req, res) => res.json(req.user));
app.listen(3000);
EOF
printf '{ "name": "auth-demo", "dependencies": { "express": "^4.19.2", "jsonwebtoken": "^9.0.2" } }\n' > package.json
