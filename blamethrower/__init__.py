# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""
BlameThrower

Library code for parsing static analysis results and revision control
attribution information.
"""

from collections import namedtuple, defaultdict
import itertools
import warnings

import blamethrower.analyzers
import blamethrower.reporeaders


__all__ = ['Analyne', 'getanalyzers', 'getreporeaders', 'getbugs', 'getblame', 'merge', 'read_analynes', 'getmodule', 'itergroup', 'NoOneToBlameWarning']
__version__ = "0.7.0"

#: A `namedtuple` describing a line of code: file, linenum, bugtype, severity, author
#: `file` is a filename string (including any path)
#: `linenum` is an int line number
#: `bugtype` is a string categorizing a bug
#: `severity` is the severity of a bug: one of 'high', 'med', 'low'
#: `author` is the author of the line
Analyne = namedtuple('Analyne', 'filename linenum bugtype severity author')        # pylint: disable=C0103


def getanalyzers():
    """:Return: the names of available static analyzers.

    :rtype: tuple(str)
    """
    return tuple(blamethrower.analyzers.__all__)


def getreporeaders():
    """:Return: the names of available repository readers.

    :rtype: tuple(str)
    """
    return tuple(blamethrower.reporeaders.__all__)


def getbugs(analyzer_name, bugsfile, **options):
    """:Return: An iterator over :class:`Analyne` tuples for the bugs found
    in `bugsfile`.

    :param str analyzer_name: The name of the module to use to read `bugsfile`.
    :param dict(str,str) options: Any keyword options to pass to the `analyze`
      method.
    """
    analyzer = getmodule("blamethrower.analyzers", analyzer_name)
    if not analyzer:
        raise ValueError("Unknown analysis file type '{0}'".format(analyzer_name))
    return blamethrower.analyzers._check_analyzer_output(analyzer.analyze(bugsfile, **options))


def getblame(repo_name, blamefile, **options):
    """:Return: a dict mapping a filename to a list of authors.

    :param str repo_name: The name of the module to use to read `blamefile`.
    :param file blamefile: VCS "blame" output from VCS `repo_name`.
    :param dict(str,str) options: Any keyword arguments for the `read` method.
    :rtype: dict(str: list(str))
    """
    reporeader = getmodule("blamethrower.reporeaders", repo_name)
    if not reporeader:
        raise ValueError("Unknown repo file type '{0}'".format(repo_name))
    return blamethrower.reporeaders._check_reporeader_output(reporeader.read(blamefile, **options))


def merge(bugs=None, blame=None):
    """:Return: an iterator over :class:`Analyne` namedtuples with all information
    on the given `bugs` and/or `blame`.

    Note there can be multiple outputs for the same line if it has multiple bugs.
    If `blame` is given and a bug has no author, the bug is returned without an author
    and a :exc:`NoOneToBlameWarning` is raised.  In particular, note that some analyzers give bugs
    for lines that don't actually exist.
    :param iter(Analyne) bugs: Iterator over Analyne namedtuples from :func:`getbugs`.
    :param iter((str, list(str))) blame: an iterable of ``(filename,  authorlist)`` pairs from :func:`getblame`.
    :raises NoOneToBlameWarning: If `bugs` and `blame` are given and there is one or more bugs with no blame.
    """
    # Assumption: each line can only have one author, but multiple bugs.  [Later: one language, one linetype]
    # This seems to be simpler and more efficient to do case-by-case
    if bugs and not blame:
        for bug in bugs:
            yield bug

    elif blame:
        file2line2bugs = defaultdict(lambda: defaultdict(list))
        for bug in bugs or []:
            file2line2bugs[bug.filename][bug.linenum].append(bug)

        for filename, authorlist in blame:
            linenum = 0
            for linenum, author in enumerate(authorlist[1:], 1):
                buglist = file2line2bugs.get(filename, {}).get(linenum)       # Tread lightly on defaultdicts
                if buglist:
                    for bug in buglist:
                        yield bug._replace(author=author)               # pylint: disable=W0212
                    del file2line2bugs[filename][linenum]
                else:
                    yield Analyne(filename=filename, linenum=linenum, bugtype=None, severity=None, author=author)

        # Output any remaining bugs with no blame, and raise warning.
        numbugs = 0
        for numbugs, bug in enumerate(itertools.chain.from_iterable(buglist for line2bugs in file2line2bugs.itervalues() for buglist in line2bugs.itervalues()), 1):
            yield bug
        if numbugs:
            warnings.warn(NoOneToBlameWarning(numbugs), stacklevel=2)

    else:
        return      # No inputs, no outputs.


def read_analynes(infile):
    """:Return: an iterator over :class:`Analyne` namedtuples read from open-for-reading
    text file `infile`."""
    for line in infile:
        filename, linenum, bugtype, severity, author = (field or None for field in line.rstrip('\n').split('\t'))
        linenum = int(linenum)
        severity = severity or None
        yield Analyne(filename, linenum, bugtype, severity, author)


def blame2analynes(blame):
    """:Return: an iterator over :class:`Analyne` namedtuples constructed from
    the output of :func:`getblame` `blame`."""
    for filename, authors in blame:
        for linenum, author in enumerate(authors[1:], 1):
            yield Analyne(filename, linenum, None, None, author)


def getmodule(package, module):
    """:Return: Dynamically import `module` from `package`, or `None` if it could not be imported."""
    # Is this polluting the namespace?
    return getattr(__import__(package, fromlist=[module]), module, None)     # Aren't Python imports fun?


def itergroup(iterable, isstart=lambda x: x):
    """Group `iterable` into groups starting with items where `isstart(item)` is true.

    Start items are included in the group.  The first group may or may not have
    a start item. An empty `iterable` results in an empty result (zero groups).
    """
    # Python's closures leave something to be desired
    def keyfunc(item):
        if isstart(item):
            keyfunc.groupnum += 1       # pylint: disable=E1101,W0612
        return keyfunc.groupnum         # pylint: disable=E1101
    keyfunc.groupnum = 0
    return (group for _, group in itertools.groupby(iterable, keyfunc))


class NoOneToBlameWarning(Warning):
    """Warning indicating that no attribution could be found for a bug."""
    def __init__(self, numbugs):
        """:param int numbugs: The number of bugs with no blame."""
        super(NoOneToBlameWarning, self).__init__("{0} bugs with no blame".format(numbugs))
        self.numbugs = numbugs


if set(getanalyzers()).intersection(set(getreporeaders())):
    raise ValueError("Analyzers and repo readers cannot share a name: {0}".format(set(getanalyzers()).intersection(set(getreporeaders()))))