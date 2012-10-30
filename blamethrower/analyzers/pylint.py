# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""
Read output of pylint -iy -rn -f parseable
http://www.logilab.org/857
"""

import re

from blamethrower import Analyne

__all__ = ['analyze', 'HELP']
HELP = 'pylint -iy -rn -fparseable'
PYLINT_RE = re.compile(r'(?P<filename>.*?):(?P<linenum>\d+): \[(?P<bugtype>[CWREF]\d{4})(,|\])')
TYPE2SEVERITY = {'C': 'low', 'R': 'low', 'W': 'med', 'E': 'high', 'F': 'high'}


def severity(bugtype):
    """:Return: The severity of `bugtype`."""
    return TYPE2SEVERITY.get(bugtype[0]) if bugtype else None


def analyze(bugfile):
    """:Return: A iterator of :class:`Analyne` describing the bugs in Pylint output `bugfile`.

    :param file bugfile: An open-for-reading Pylint "parseable" (``-f parseable``) output file
      with message IDs included (``-iy``) and full report excluded (``-rn``).
    :rtype: iter(namedtuple)
    """
    for linenum, line in enumerate(bugfile, 1):
        match = PYLINT_RE.match(line)
        if match:
            filename, linenum, bugtype = match.group('filename', 'linenum', 'bugtype')
            yield Analyne(filename, int(linenum), bugtype, severity(bugtype), None)
        elif linenum == 1:
            raise ValueError('Could not parse first line of pylint output')
