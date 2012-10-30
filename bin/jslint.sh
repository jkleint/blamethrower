#!/bin/bash
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Generate jslint bug report for all js files under the current directory.

JAR=jslint4java.jar     # Change me
find * -name '*.js' | xargs java -jar "$JAR" --maxerr 100000
