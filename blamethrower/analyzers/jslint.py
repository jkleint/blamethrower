# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""
jslint4java parser.

jslint4java is simple on the face of it:

    jslint:filename:linenum:charnum:message

However, there can be colons in filenames; by default it stops after a few
errors, and even when you tell it 'More!' it chokes on valid JavaScript; bugs
aren't categorized; sometimes messages contain newlines; and it has a nasty
habit of giving line numbers that don't exist for errors at end of file.
"""

import re

from blamethrower import Analyne


__all__ = ['analyze', 'HELP']
HELP = 'jslint4java --maxerr 100000'
JSLINT_RE = re.compile(r'^jslint:(?P<filename>.+?):(?P<linenum>\d+):\d+:(?P<bugtype>.+)')


def analyze(bugsfile):
    """:Return: an iterator over :class:`blamethrower.Analyne` namedtuples describing
    the bugs found in jslint4java default output `bugsfile`.

    Bug "types" currently aren't very useful, since they're just the specific error message,
    and no severity is assigned.
    """
    for linenum, line in enumerate(bugsfile, 1):
        match = JSLINT_RE.search(line)
        if match:
            # TODO: Categorize bugs... I guess just regexp matching the message?
            yield Analyne(match.group('filename'), int(match.group('linenum')), match.group('bugtype'), severity=None, author=None)
        elif linenum == 1:
            raise ValueError("Unable to parse first line of jslint output")
