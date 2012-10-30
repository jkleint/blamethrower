# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""BlameThrower analyzer unit tests."""

import unittest

from test import AnalyneTest


class AnalyzerTests(AnalyneTest):
    def test_httpbin_pylint(self):
        self.assert_analynes_equal('analyzers', 'pylint', 'httpbin')

    def test_shove_pylint(self):
        self.assert_analynes_equal('analyzers', 'pylint', 'shove')

    def test_apricot_jslint(self):
        self.assert_analynes_equal('analyzers', 'jslint', 'apricot')

    def test_os_utils_findbugs(self):
        self.assert_analynes_equal('analyzers', 'findbugs', 'os-utils')


if __name__ == "__main__":
    unittest.main()