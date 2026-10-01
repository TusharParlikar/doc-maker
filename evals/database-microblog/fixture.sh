#!/usr/bin/env bash
# Pinned fixture: miguelgrinberg/microblog @ a975ef64864354867c88e0ed3a17ba7d17dca752
set -euo pipefail
git init -q .
git remote add origin https://github.com/miguelgrinberg/microblog.git
git fetch -q --depth 1 origin a975ef64864354867c88e0ed3a17ba7d17dca752
git checkout -q FETCH_HEAD
