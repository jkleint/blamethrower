# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""
Get line authorship attribution from git.

Here's why this is somewhat challenging: ``git blame`` is designed to work on
one file at a time, with the implication that you know what file it's talking
about, since you gave it the filename.  However, when you run together the
output from ``git ls-files | xargs -L1 git blame --porcelain``, you have
to figure out which file it's talking about.  And unfortunately, commits
before a file rename use the old name; the only way to get accurate commit
attribution is to add a header with the filename before the output for each
file.  Thus, we rely on a helper script to add headers.
See `bin/git-blame.sh`.
"""

import re

from blamethrower import itergroup

__all__ = ['read', 'HELP']
HELP = 'git blame -p with headers; see bin/git-blame.sh'
GIT_HEADER_RE = re.compile(r"^>>> git-blame output for: (?P<filename>.+) <<<$")
# Skip empty files, for which git-blame arguably gives the incorrect line number 1
GIT_PORCELAIN_RE = re.compile(r"""^(?P<commit>[0-9a-f]{40}) \d+ (?P<linenum>\d+)( [1-9][0-9]*)?
(author (?P<author>.+)$)?""", re.MULTILINE)


def get_authors(porcelain):
    """:Return: an iterable of authors for each line of source code in git-blame output.

    :param iter(str) porcelain: The output from ``git blame --porcelain``
      on one file.
    :rtype: iter(str)
    """
    commit2author = {}
    yield None      # "line 0" has no author
    for expected_linenum, match in enumerate(GIT_PORCELAIN_RE.finditer(''.join(porcelain)), 1):
        linenum, author, commit = match.group('linenum', 'author', 'commit')
        linenum = int(linenum)
        if author is None:
            author = commit2author.get(commit)
            assert author
        else:
            author = intern(author)     # Save some memory
            assert commit2author.get(commit) in (None, author)
            commit2author[commit] = author
        assert linenum == expected_linenum, "Expected line number {0} in commit {1}; got {2}".format(expected_linenum, commit, linenum)
        yield author


def read(blamefile):
    """Iterate over source files described by git-blame output with headers.

    :Return: An iterator of ``(filename, list(author))`` tuples, with ``list[i]``
      being the author of line ``i`` in `filename`.
    :rtype: iter((str, list(str)))
    """
    def getfilename(line):
        """:Return: the filename from a header `line`, or `None` if `line` was not a header."""
        match = GIT_HEADER_RE.match(line)
        return match.group('filename') if match else None

    # This doesn't use REs so we can stream the file, since a multi-line RE
    # would require reading in the whole file, or stitching chunks.
    for sourcefile in itergroup(blamefile, getfilename):
        filename = getfilename(next(sourcefile))
        if not filename:
            raise ValueError("Did not find header as first line of git blame output")
        yield filename, list(get_authors(sourcefile))
