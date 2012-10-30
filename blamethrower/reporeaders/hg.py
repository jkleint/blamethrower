# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""
Read (augmented) Mercurial ``hg blame -vu``  output.

Mercurial's output, while simple, is pretty hopeless on its own.

1. It gives the old filename on renames.
2. It separates fields with spaces and colons, but allows spaces and colons in usernames and filenames,
   and right-justifies usernames with spaces.  This makes it impossible to parse reliably, and they
   don't intend to fix it: http://bz.selenic.com/show_bug.cgi?id=3217
3. It doesn't output the username for binary files.
4. usernames are stored as UTF-8, but filenames (and contents) are stored as binary blobs.
5. Bonus un-feature: it truncates brief-form usernames (without -v) at the first non-alnum character.

So, we can't use the output of Mercurial directly.  Before it gets here, we need
to help it by filtering out binary files and prepending a header to the output
for each file. See `bin/hg-blame.sh`.  The output is just a header line followed
by an author name for each line in the file.
"""

import re

from blamethrower import itergroup

__all__ = ['read', 'HELP']
HELP = 'hg blame with headers; see bin/hg-blame.sh'
HEADER_RE = re.compile(r"^>>> hg blame output for: (?P<filename>.+) <<<$")
AUTHOR_RE = re.compile(r"^\s*(?P<author>.+?)( <.+@.+>)?\s*$")


def read(blamefile):
    """Iterate over source files described by ``hg blame -vu`` output that has
    has headers and does not have binary files.

    Empty files are skipped.
    :Return: An iterator of ``(filename, list(author))`` tuples, with ``list[i]``
      being the author of line ``i`` in `filename`.
    :rtype: iter((str, list(str)))
    """
    def getfilename(line):
        """:Return: the filename from a header `line`, or `None` if `line` was not a header."""
        match = HEADER_RE.match(line)
        return match.group('filename') if match else None

    for sourcefile in itergroup(blamefile, getfilename):
        filename = getfilename(next(sourcefile))
        if not filename:
            raise ValueError("Did not find header as first line of hg blame output")
        authors = [None]
        for line in sourcefile:
            match = AUTHOR_RE.match(line)
            if not match:
                raise ValueError("Could not parse author from hg blame output for '{0}'".format(filename))
            authors.append(match.group('author'))
        if len(authors) > 1:
            yield filename, authors
