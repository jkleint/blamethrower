#!/bin/bash
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Collect authorship attribution for every line in every file of (the HEAD of) 
# the git repository in the current directory.

# We have to add a header with the filename before each file, since git outputs 
# the old filename on renames.

HEADER=">>> git-blame output for: {} <<<"
XARGS="$(which parallel || echo "xargs -I{} bash -c")"
git ls-tree --name-only --full-tree -rz HEAD | $XARGS -0 "echo '$HEADER' ; git blame -wC --porcelain -- '{}'"
