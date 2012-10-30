# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""BlameThrower source code repository reader unit tests."""

import unittest

from test import AnalyneTest


class RepoReaderTests(AnalyneTest):
    def test_httpbin_git(self):     # https://github.com/kennethreitz/httpbin 15d132f76e687fcae229dd63df7a3452aa241e1d 2012 Sep 09
        self.assert_analynes_equal('reporeaders', 'git', 'httpbin')

    def test_apricot_git(self):     # https://github.com/silentrob/Apricot e5d0c711566c9e4ff690f672e63833b72bc76fe6 2012 Jul 26
        self.assert_analynes_equal('reporeaders', 'git', 'apricot')

    def test_shove_hg(self):        # https://bitbucket.org/lcrees/shove 6d9200daacef4fc24f522314eb8f6b22d6fc72f4 2012 Oct 01
        self.assert_analynes_equal('reporeaders', 'hg', 'shove')

    def test_os_utils_git(self):    # https://github.com/casser/os-utils 637015569b2bf8e2d83406e234b5e8d667b06193 2012 Sep 05
        self.assert_analynes_equal('reporeaders', 'git', 'os-utils')


if __name__ == "__main__":
    unittest.main()