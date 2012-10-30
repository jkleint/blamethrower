# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""
BlameThrower stats.

- per-author, unattributed, and overall:
  - files
  - lines
  - bugs
    - total
    - high
    - med
    - low
  - bugs_per_line

"""

from __future__ import division
from collections import defaultdict
import copy

__all__ = ['getstats']


def getstats(analynes):
    """:Return: a dictionary giving all available statistics about the bugs and/or
    blame in `analynes`.

    Bugs without a (valid) severity count toward the total, so high + med +
    low will not add up to total.
    """
    # Do recall: there can be multiple analynes for the same line of code.
    # We make no attempt to deduplicate bugs.
    AUTHOR = {
        'lines': defaultdict(lambda: set()),
        'bugs': {'total': 0, 'high': 0, 'med': 0, 'low': 0},
        'files': set(),
        'bugs_per_line': 0.0,
    }

    overall =  {
        'lines': 0,
        'bugs': {'total': 0, 'high': 0, 'med': 0, 'low': 0},
        'files': set(),
        'bugs_per_line': 0.0,
    }

    authors = defaultdict(lambda: copy.deepcopy(AUTHOR))
    for analyne in analynes:
        stats = authors[analyne.author]
        stats['lines'][analyne.filename].add(analyne.linenum)
        if analyne.bugtype:
            stats['bugs'][analyne.severity or 'total'] += 1
        stats['files'].add(analyne.filename)

    for stats in authors.itervalues():
        overall['files'].update(stats['files'])
        stats['lines'] = sum(len(lines) for lines in stats['lines'].itervalues())
        stats['bugs']['total'] += stats['bugs']['high'] + stats['bugs']['med'] + stats['bugs']['low']
        stats['files'] = len(stats['files'])
        stats['bugs_per_line'] = stats['bugs']['total'] / stats['lines'] if stats['lines'] else 0

        overall['lines'] += stats['lines']
        for type_ in ('total', 'high', 'med', 'low'):
            overall['bugs'][type_] += stats['bugs'][type_]

    overall['files'] = len(overall['files'])
    overall['bugs_per_line'] = overall['bugs']['total'] / overall['lines'] if overall['lines'] else 0

    result = {
        'overall': overall,
        'unattributed': authors.pop(None, dict(AUTHOR, lines=0, files=0)),
        'authors': {},
    }
    if authors:
        result['authors'] = dict(authors)
    return result
