#!/bin/bash
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Collect authorship attribution for every line in every file of (the tip of) 
# the Mercurial repository in the current directory.

# We have to add a header with the filename before each file, since Mercurial outputs 
# the old filename on renames.

HEADER=">>> hg blame output for: {} <<<"
XARGS=(xargs -I{})
if which parallel > /dev/null; then XARGS=(parallel -q); fi
hg manifest | "${XARGS[@]}" bash -c "echo '$HEADER'; hg blame -vu '{}' | grep -vx '{}: binary file' | cut -f1 -d:"
