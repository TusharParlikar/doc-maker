#!/usr/bin/env bash
# Pinned fixture: fastapi/full-stack-fastapi-template @ cb740b656d7a0a6c5e12c7bf8e50343ec94ee9c7
set -euo pipefail
git init -q .
git remote add origin https://github.com/fastapi/full-stack-fastapi-template.git
git fetch -q --depth 1 origin cb740b656d7a0a6c5e12c7bf8e50343ec94ee9c7
git checkout -q FETCH_HEAD
