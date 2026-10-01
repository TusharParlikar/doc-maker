#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'EOF'
{ "name": "todo-api", "version": "0.1.0", "main": "server.js",
  "scripts": { "start": "node server.js" },
  "dependencies": { "express": "^4.19.2" } }
EOF
cat > server.js <<'EOF'
const express = require('express');
const app = express();
app.use(express.json());

const todos = []; // in memory: lost on restart

app.get('/todos', (req, res) => res.json(todos));

app.post('/todos', (req, res) => {
  const todo = { id: todos.length + 1, title: req.body.title, done: false };
  todos.push(todo);
  res.status(201).json(todo);
});

app.listen(process.env.PORT || 3000);
EOF
