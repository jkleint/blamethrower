#!/bin/bash
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Generate pylint bug report for all python files under the current directory.

find * -name '*.py' | xargs --no-run-if-empty pylint -iy -rn -fparseable
