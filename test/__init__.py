# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""BlameThrower common testing code."""

import os.path
from bz2 import BZ2File
import unittest
from itertools import izip_longest, chain
import warnings

from blamethrower import read_analynes, getbugs, getblame, blame2analynes, merge


def open_datafile(package, filename):
    """:Return: An open file object for the given bz2-compressed (base) `filename` in
    test package `package`."""
    filename = os.path.join(os.path.dirname(__file__), package, filename)
    return BZ2File(filename, 'rU')


class AnalyneTest(unittest.TestCase):
    """Compares actual to expected Analynes read from datafiles."""
    @staticmethod
    def readbugs(analyzer2project, options=None):
        """:Return: an iterable of Analynes read from the test data files for each analyzer and project in `analyzer2project`.

        :param dict(str,str) analyzer2project: Map of analyzer names to test project names.
        :param dict(str,dict(str,str)) options: Map of module names to map of module options to values.

        """
        return chain.from_iterable(getbugs(analyzer, open_datafile('analyzers', '{0}.{1}.txt.bz2'.format(project, analyzer)), **(options or {}).get(analyzer, {})) for analyzer, project in sorted(analyzer2project.iteritems()))

    @staticmethod
    def readblame(repo2project, options=None):
        """:Return: an iterable of ``(filename, list(author))`` pairs read from the test data files for each repo and project in `repo2project`.

        :param dict(str,str) repo2project: Map of reporeader names to test project names.
        :param dict(str,dict(str,str)) options: Map of module names to map of module options to values.
        """
        return chain.from_iterable(getblame(repo, open_datafile('reporeaders', '{0}.{1}.txt.bz2'.format(project, repo)), **(options or {}).get(repo, {})) for (repo, project) in sorted(repo2project.iteritems()))

    def assert_sets_equal(self, expected, actual):
        """Assert `expected` is equal to `actual` and print useful message if not."""
        for item in expected:
            self.assertTrue(item in actual, "Did not find expected item {0} in actual set".format(item))
        for item in actual:
            self.assertTrue(item in expected, "Found extra item {0} in actual set".format(item))

    def assert_analynes_equal(self, package, module, project, options=None):
        """Assert that actual data parsed from analyzer or reporeader
        `package.module` matches the expected data for `project`.

        Assumes actual and expected data are in the same order.
        :param str pacakge: 'analyzer' or 'reporeader'
        :param str module: The name of an anlyzer or reporeader
        :param str project: Parse actual Analynes from file ``package/project.module.txt.bz2``;
          get expected Analynes from ``package/project.module.tsv.bz2``.
        :param dict(str,str) options: Any kwargs to pass to the `read` or `analyze` function of `module`.
        """
        expected_filename = '{0}.{1}.tsv.bz2'.format(project, module)
        if package == 'analyzers':
            actual = self.readbugs({module: project}, options)
            expected = read_analynes(open_datafile('analyzers', expected_filename))
        elif package == 'reporeaders':
            actual = blame2analynes(self.readblame({module: project}, options))
            expected = read_analynes(open_datafile('reporeaders', expected_filename))
        else:
            assert False

        for expected, actual in izip_longest(expected, actual):
            self.assertEqual(expected, actual)

    def assert_merge_works(self, repo2project, analyzer2project, options=None):
        """Assert that all the bugs and blame given are present, and no more, in the
        output of :func:`merge`.

        :param dict(str,str) repo2project: Map of reporeader names to test project names.
        :param dict(str,str) analyzer2project: Map of analyzer names to test project names.
        :param dict(str,dict(str,str)) options: Map of module names to map of module options to values.
        """
        # This assumes getbugs() and getblame() work correctly.  :)
        # TODO: This might not completely test duplicate bugs or blame.
        bugs = set(self.readbugs(analyzer2project, options))
        blame = list(self.readblame(repo2project, options))
        with warnings.catch_warnings(record=True) as warnlist:
            merged = list(merge(bugs, blame))

        actualbugs = set(bug._replace(author=None) for bug in merged if bug.bugtype)        # pylint: disable=W0212
        self.assert_sets_equal(bugs, actualbugs)

        expectedblame = set(blame2analynes(blame))
        # All blame except bugs that do not correspond to any known line; this sort of assumes merge doesn't hose the authors.
        actualblame = set(line._replace(bugtype=None, severity=None) for line in merged if not (line.bugtype and line._replace(bugtype=None, severity=None) not in expectedblame))     # pylint: disable=W0212
        self.assert_sets_equal(expectedblame, actualblame)

        # Check that we issued the right Warning if there were bugs with no attribution
        blameless_bugs = [bug for bug in merged if bug.bugtype and not bug.author]
        if blameless_bugs:
            self.assertEqual(len(warnlist), 1)
            self.assertEqual(str(warnlist[0].message), '{0} bugs with no blame'.format(len(blameless_bugs)))
        else:
            self.assertFalse(warnlist)