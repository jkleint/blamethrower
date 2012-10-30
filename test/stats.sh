#!/bin/bash
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Read BlameThrower TSV on stdin and compute stats with stone tools.  Just to be sure.
# Warning: Contains Unix.™

set -eo pipefail
export LC_ALL=C

function tabify {
    sed -r 's/^ *([0-9]+) /\1\t/'
}
function lines_by_author {
    awk -F$'\t' -vOFS=$'\t' '{print $5, $1, $2, $3, $4}' | sort -t$'\t' -k1,3 -u | cut -f1 | uniq -c | tabify
}
function files_by_author {
    awk -F$'\t' -vOFS=$'\t' '{print $5, $1, $2, $3, $4}' | sort -t$'\t' -k1,3 -u | cut -f1,2 | uniq | cut -f1 | uniq -c | tabify
}
function bugs_by_author {
    grep -xE $'[^\t]*\t[^\t]*\t[^\t]+\t[^\t]*\t.*' | cut -f5 | sort | uniq -c | tabify
}
function total_lines {
    sort -t$'\t' -k1,2 -u | wc -l
}
function total_files {
    cut -f1 | sort -u | wc -l
}
function total_bugs {
    grep -cxE $'[^\t]*\t[^\t]*\t[^\t]+\t[^\t]*\t.*'
}

input=$(mktemp blamethrower.tmp.XXXXXX)
cat > "$input"

echo $'author\tlines\tfiles\tbugs'
join -t$'\t' -11 -22 -a1 -a2 <(join -t$'\t' -j 2 -a1 -a2 <(lines_by_author < "$input") <(files_by_author < "$input")) <(bugs_by_author < "$input")

echo -e "\n<total>\t$(total_lines < "$input")\t$(total_files < "$input")\t$(total_bugs < "$input")"

rm "$input"
