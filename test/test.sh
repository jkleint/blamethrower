#!/bin/bash
# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

# Run BlameThrower tests.

set -eo pipefail
dir="$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")")"

cd "$dir"
unittest=$(which unit2 || echo "python -m unittest")
$unittest discover

echo -e "\nFunctional tests"
blamethrower=("$dir/bin/blamethrower")
export PYTHONPATH=$PYTHONPATH:"$dir"
function statsfilter {
    sed '1,/  }, /d'    # Delete args, version, timestamp at start of stats output
}
cd "$dir"/test
errfile=blamethrower.err
outfile=blamethrower.out
IFS=.       # Ahh, the joys of bash string manipulation. :)

# Single module functional tests.
for infile in {reporeaders,analyzers}/*.txt.bz2; do
    parts=($infile)
    module="${parts[1]}"
    parts[2]=tsv
    datafile="${parts[*]}"
    parts[2]=json
    statfile="${parts[*]}"
    "${blamethrower[@]}" --rawdata "--$module" <(bzcat "$infile") | tail -n+2 > "$outfile"
    diff -u0 --label="$datafile" <(bzcat "$datafile") "$outfile"
    "${blamethrower[@]}" "--$module" <(bzcat "$infile") > "$outfile"
    diff -u0 --label="$statfile" <(bzcat "$statfile" | statsfilter) --label="$outfile" <(statsfilter < "$outfile")
    echo -n .
done

# Multimodule functional tests.
for datafile in *.tsv.bz2; do
    parts=($datafile)
    project="${parts[0]}"
    repo="${parts[1]}"
    analyzer="${parts[2]}"
    parts[3]=json
    statfile="${parts[*]}"
    "${blamethrower[@]}" --rawdata $(cat "$project.$repo.$analyzer.opts" 2>/dev/null) "--$repo" <(bzcat reporeaders/"$project.$repo.txt.bz2") "--$analyzer" <(bzcat analyzers/"$project.$analyzer.txt.bz2") 2> "$errfile" | tail -n+2 > "$outfile"
    diff -u0 --label="$datafile" <(bzcat "$datafile") "$outfile"
    diff -u0 "$(ls "$project.$repo.$analyzer.err" 2>/dev/null || ls /dev/null)" "$errfile"
    "${blamethrower[@]}" $(cat "$project.$repo.$analyzer.opts" 2>/dev/null) "--$repo" <(bzcat reporeaders/"$project.$repo.txt.bz2") "--$analyzer" <(bzcat analyzers/"$project.$analyzer.txt.bz2") 2> "$errfile" > "$outfile"
    diff -u0 --label="$statfile" <(bzcat "$statfile" | statsfilter) --label="$outfile" <(statsfilter < "$outfile")
    diff -u0 "$(ls "$project.$repo.$analyzer.err" 2>/dev/null || ls /dev/null)" "$errfile"
    echo -n .
done

rm "$errfile" "$outfile"
echo -e "\nOK"
