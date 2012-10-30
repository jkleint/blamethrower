#!/usr/bin/awk -f
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Convert mercurial blame with headers to Analyne TSV.

BEGIN { OFS="\t" }
{
	if (match($0, "^>>> hg blame output for: (.+) <<<$", groups)) {
		filename=groups[1]
		linenum=0
	}
	else {
		match($0, "^[[:space:]]*(.+) <.*@.*>$", groups)
		linenum += 1
		print filename, linenum, "", "", groups[1]
	}
}
