# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""BlameThrower modules for reading the output of static anaysis tools."""

__all__ = ['findbugs', 'jslint', 'pylint']


import blamethrower

_MAX_VALID_LINENUM = 1000000

if __debug__:
    def _check_analyzer_output(analynes):
        """Verify that `analynes` have a filename, linenum, and bugtype, and
        pass them through.

        :param iter(Analyne) analynes: Iterable of Analynes to validate.
        :rtype: iter(Analyne)
        """
        for analyne in analynes:
            assert analyne.filename
            assert isinstance(analyne.linenum, int) and 0 < analyne.linenum < _MAX_VALID_LINENUM
            assert analyne.bugtype
            assert analyne.severity in (None, 'high', 'med', 'low')
            yield analyne
else:
    # Yes, I timed it and this really is faster, even with -O.
    def _check_analyzer_output(analynes):
        return analynes
