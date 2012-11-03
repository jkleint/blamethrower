# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""
Parse FindBugs -xml:withMessages output.

FindBugs XML output is pretty straightforward: a sequence of <BugInstance> tags,
with type and rank (severity) attributes.  Each has one or more <SourceLine>
tags; if more, one will have an attribute of primary="true".  However, it groups
nearby bugs of the same type via another <SourceLine> with
role="SOURCE_LINE_ANOTHER_INSTANCE". Also, each <SourceLine> can be a range of
lines, so we just pick the first.

The only other issues are that FindBugs works on compiled binaries, so the
source file names may not line up with your repo blame filenames; and it
sometimes outputs duplicate bugs.
"""

from xml.etree import ElementTree
from itertools import ifilter

from blamethrower import Analyne

__all__ = ['analyze', 'HELP', 'OPTIONS']
HELP = 'FindBugs -xml:withMessages'
OPTIONS = {'prefix': 'add path prefix to FindBugs filenames'}


def rank2severity(rank):
    """:Return: the BlameThrower severity for a bug of the given `rank`."""
    if 1 <= rank <= 4:
        return 'high'
    elif rank <= 12:
        return 'med'
    elif rank <= 20:
        return 'low'
    else:
        assert False


def analyze(bugsfile, prefix=''):
    """:Return: an iterable of :class:`Analyne` objects read from FindBugs
    -xml:withMessages file `bugsfile`.

    :param str prefix: A path prefix to prepend to every filename.
    """
    for _, bug in ifilter(lambda event_elt: event_elt[1].tag == 'BugInstance', ElementTree.iterparse(bugsfile)):
        bugtype = bug.get('type')
        severity = rank2severity(int(bug.get('rank')))
        sourcelines = bug.findall('SourceLine')
        assert sourcelines, "No SourceLine for bug: {}".format(bug.attrib)
        if len(sourcelines) > 1:
            sourcelines = [line for line in sourcelines if line.attrib.get('primary') or line.attrib.get('role') == 'SOURCE_LINE_ANOTHER_INSTANCE']
            assert sourcelines, "No SourceLine for bug: {}".format(bug.attrib)
        for sourceline in sourcelines:
            filename = prefix + sourceline.get('sourcepath')
            linenum = sourceline.get('start')
            yield Analyne(filename, int(linenum), bugtype, severity, None)
        bug.clear()
