#!/bin/bash
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Generate Analyne blame TSV for every non-empty file in the current git repo.

dir="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
git ls-tree --name-only --full-tree -rz HEAD | xargs -0 -I{} bash -c "test -s '{}' && git blame -wC --line-porcelain -- '{}' | awk '-vfilename={}' -f \"$dir\"/git-line-porcelain-to-tsv.awk"
