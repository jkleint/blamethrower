#!/usr/bin/awk -f
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Read git blame --line-porcelain output for ONE file, output as Analyne TSV.
# Needs a "filename" variable set with -vfilename=whatever
# Gives incorrect output on blame for empty files.

BEGIN {OFS="\t"}
match($0, "^author (.+)$", groups) { linenum +=1 ; print filename, linenum, "", "", groups[1] }
