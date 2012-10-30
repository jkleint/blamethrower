# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""BlameThrower library code unit tests."""

from __future__ import division
import unittest
import itertools
import random
from collections import defaultdict
import warnings

import blamethrower.stats
from test import AnalyneTest


class BlamethrowerTest(AnalyneTest):
    @staticmethod
    def get_correct_stats(analynes, filterfunc=lambda analyne: True):
        """:Return: a stats dict for all `analynes` for which ``filterfunc(analyne)`` is truthy."""
        file2lines = defaultdict(set)
        bugs = {
            'high': 0,
            'med': 0,
            'low': 0,
            'total': 0
        }
        for analyne in itertools.ifilter(filterfunc, analynes):
            file2lines[analyne.filename].add(analyne.linenum)
            if analyne.bugtype:
                bugs['total'] += 1
                if analyne.severity:
                    bugs[analyne.severity] += 1

        lines = sum(len(lines) for lines in file2lines.itervalues())
        return {
            'files': len(file2lines),
            'lines': lines,
            'bugs': bugs,
            'bugs_per_line': bugs['total'] / lines if lines else 0
        }

    def _assert_stats_correct(self, stats, analynes, num_blameless_bugs):
        """Assert that `stats` are correct for the given `analynes`.

        :param dict stats: The output of :meth:`getstats`.
        :param int num_blameless_bugs: The number of bugs with no author to expect (when blame is provided).
        """
        analynes = list(analynes)
        self.assertEqual(self.get_correct_stats(analynes), stats['overall'])
        authors = set(analyne.author for analyne in analynes if analyne.author is not None)
        if not authors:       # No blame provided
            self.assertFalse(stats['authors'])
            self.assertEqual(stats['overall'], stats['unattributed'])
        else:
            for author in authors:
                self.assertEqual(self.get_correct_stats(analynes, lambda a: a.author == author), stats['authors'][author])
            self.assertEqual(len(authors), len(stats['authors']))
            self.assertEqual(self.get_correct_stats(analynes, lambda a: a.author is None), stats['unattributed'])
            self.assertEqual(num_blameless_bugs, stats['unattributed']['bugs']['total'])

    def assert_stats_correct(self, repo2project, analyzer2project, options=None):
        """Assert that :func:`getstats` is correct for the given bugs and blame.

        :param dict(str,str) repo2project: Map of reporeader names to test project names.
        :param dict(str,str) analyzer2project: Map of analyzer names to test project names.
        :param dict(str,dict(str,str)) options: Map of module names to map of module options to values.
        """
        bugs = self.readbugs(analyzer2project, options)
        blame = self.readblame(repo2project, options)
        blameless_bugs = 0
        with warnings.catch_warnings(record=True) as warnlist:
            analynes = list(blamethrower.merge(bugs, blame))
        if warnlist:
            warning = warnlist[0].message
            self.assertTrue(isinstance(warning, blamethrower.NoOneToBlameWarning))
            blameless_bugs = warning.numbugs

        self._assert_stats_correct(blamethrower.stats.getstats(analynes), analynes, blameless_bugs)

    def test_stats(self):
        self.assert_stats_correct({'git': 'httpbin'}, {'pylint': 'httpbin'})
        self.assert_stats_correct({'git': 'apricot'}, {'jslint': 'apricot'})
        self.assert_stats_correct({'hg': 'shove'}, {'pylint': 'shove'})
        self.assert_stats_correct({'git': 'os-utils'}, {'findbugs': 'os-utils'}, {'findbugs': {'prefix': 'src/'}})

    def test_merge(self):
        self.assert_merge_works({'git': 'httpbin'}, {'pylint': 'httpbin'})
        self.assert_merge_works({'git': 'apricot'}, {'jslint': 'apricot'})
        self.assert_merge_works({'hg': 'shove'}, {'pylint': 'shove'})
        self.assert_merge_works({'git': 'os-utils'}, {'findbugs': 'os-utils'}, {'findbugs': {'prefix': 'src/'}})

    def test_itergroup(self):
        MAXINT, MAXLEN, NUMTRIALS = 100, 10000, 50
        isstart = lambda x: x == 0
        groupfunc = blamethrower.itergroup
        self.assertEqual(next(groupfunc([], isstart), None), None)
        self.assertEqual([list(grp) for grp in groupfunc([0] * 3, isstart)], [[0]] * 3)
        self.assertEqual([list(grp) for grp in groupfunc([1] * 3, isstart)], [[1] * 3])
        self.assertEqual(len(list(groupfunc([0, 1, 2] * 3, isstart))), 3)        # Catch hangs when groups are not consumed
        for _ in xrange(NUMTRIALS):
            expected, items = itertools.tee(itertools.starmap(random.randint, itertools.repeat((0, MAXINT), random.randint(0, MAXLEN))))
            for grpnum, grp in enumerate(groupfunc(items, isstart)):
                start = next(grp)
                self.assertTrue(isstart(start) or grpnum == 0)
                self.assertEqual(start, next(expected))
                for item in grp:
                    self.assertFalse(isstart(item))
                    self.assertEqual(item, next(expected))


if __name__ == "__main__":
    unittest.main()