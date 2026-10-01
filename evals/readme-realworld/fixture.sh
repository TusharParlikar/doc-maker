#!/usr/bin/env bash
# Pinned fixture: gothinkster/node-express-realworld-example-app @ 30b68e1e881462b2f4164ea09ab4c4f5699c7b0b
set -euo pipefail
git init -q .
git remote add origin https://github.com/gothinkster/node-express-realworld-example-app.git
git fetch -q --depth 1 origin 30b68e1e881462b2f4164ea09ab4c4f5699c7b0b
git checkout -q FETCH_HEAD
