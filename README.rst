BlameThrower
============
.. image:: https://travis-ci.org/jkleint/blamethrower.png
  :alt: Travis CI build status
  :target: https://travis-ci.org/jkleint/blamethrower
  :align: right

Static analysis meets ``git-blame``. ::

    $ cd project
    $ git-blame.sh > blame.txt
    $ pylint project > bugs.txt
    $ blamethrower --git blame.txt --pylint bugs.txt

::

    {
      "authors": {
        "Jay Q. Hacker": {
          "bugs": { "high": 0, "low": 1, "med": 0, "total": 1 },
          "bugs_per_line": 0.083333333333333329,
          "files": 3,
          "lines": 12
        },
        "l33t h4x0r": {
          "bugs": { "high": 1, "low": 19, "med": 1, "total": 21 },
          "bugs_per_line": 0.01057934508816121,
          "files": 15,
          "lines": 1985
        }
      },
      "overall": {
        "bugs": { "high": 1, "low": 20, "med": 1, "total": 22 },
        "bugs_per_line": 0.011016524787180772,
        "files": 16,
        "lines": 1997
      }
    }

BlameThrower combines source code repository annotations (who wrote what line)
with static analysis (which lines have bugs) to put names on bugs.

Supports git, hg, pylint, jslint, findbugs, and it's easy to add more.  Use
multiple static analysis tools and multiple repositories.  Give it blame info
to just get author stats, or bug info to get just bug stats.  Can provide raw
line-by-line authorship and bug information from multiple tools in a unified
format for any code analysis task.


Running
-------
You'll likely want to tailor static analysis with the options you care about,
and perhaps exclude some files from blame annotation (libraries, minified code,
etc.).

For static analysis, you can start with the appropriate script in ``bin/``, set
the options you like, and keep the same output format options.  Run it on your
repo and save the output in a text file.

For blame annotations, you'll need to run a helper script, since blame tools
aren't designed to operate on a whole repo.  You can start with the script for
your repo type in ``bin/<repo>-blame.sh``, and tailor it to exclude
uninteresting files.  (These scripts basically just prepend a header to the
blame output for each file.)  Run it on your repo and save the output in a text
file.

To run BlameThrower from a source checkout, source ``bin/env-setup.sh``.  Then
run ``blamethrower`` on the static analysis results and annotations.  For
example, with a git repo and pylint analysis, you'd run::

    $ blamethrower --git blame.txt --pylint pylint.txt

By default, BlameThrower outputs bug and/or blame stats to standard output in
`JSON <http://json.org>`_ format.


Caveat Blamer
-------------
Repository annotation tools aren't perfect: they sometimes blame the wrong
person for a line of code (e.g., you changed the order of lines written by
someone else, or tidied up formatting or whitespace).

Static analysis tools aren't perfect either: they generate many false
positives, and miss real bugs.   Some languages are a lot more amenable to
static analysis (like, say, the static ones ;), and some analysis tools are
more thorough than others.

Wantonly combining the two has a large potential for misinformation.  Before
you go charging down the hall, finger a-pointing, *look at the code.*  Fix the
bugs, hush the false positives.

The point of this tool is to raise awareness about static analysis, not provide
ammunition for blamewars.  Humans are naturally competitive suckers for Top 10
lists.  By putting a name on a bug and stacking people up with their peers,
maybe we can motivate people to look at bugs and fix them.


Identifying Authors
-------------------
When you look at the output, you may notice that the same person has listed
their name differently in different commits, and so their bugs are spread out
over several "authors."

In Git, you can fix this by setting up a ``.mailmap`` file in your repo as
described in the `git-blame manual page <http://git-scm.com/docs/git-blame>`_.
Then re-run BlameThrower with the new blame output and bugs will be attributed
correctly.

In Mercurial, the equivalent involves creating a new, incompatible repo with
the `convert extension
<http://mercurial.selenic.com/wiki/ConvertExtension#A--authors>`_.  This isn't
a problem if you're just modifying a private copy, but if you're changing the
"master," it will invalidate all existing copies of and references to the repo.
You may find it simpler and more efficient to just apply a mail map to the
output of ``hg-blame.sh``.


Raw Output
----------
You can get BlameThrower to give you nice parseable blame and bugs for every
line in your project with the ``--rawdata`` option::

    $ blamethrower --rawdata --git blame.txt --pylint bugs.txt

::

    filename        linenum  bugtype  severity  author
    .gitignore      1                           Jay Q. Hacker
    .gitignore      2                           Jay Q. Hacker
    setup.py        1        C0111    low       l33t h4x0r
    setup.py        2                           l33t h4x0r
    setup.py        3                           Jay Q. Hacker
    setup.py        4                           l33t h4x0r
    setup.py        5        E0611   high       l33t h4x0r

The output is tab-separated values (with tabs and newlines escaped as ``\t``
and ``\n``) for every line in the repo.  BlameThrower takes care of unifying
data from different repositories and static analysis tools, which you can then
use in your own analyses.  All of this functionality is also available via a
nice Python API.

Note that source lines can appear more than once if they have more than one
bug, and some static analysis tools output bugs for non-existent lines (I'm
looking at you, `jslint <http://www.jslint.com/>`_!).


Extending
---------
It's easy to add a module for your favorite `static analysis tool
<https://en.wikipedia.org/wiki/List_of_tools_for_static_code_analysis>`_.  Have
a look in ``blamethrower/analyzers/``, read the bit below, and `submit a pull
request <https://github.com/jkleint/blamethrower>`_!

Adding a New Analyzer
~~~~~~~~~~~~~~~~~~~~~
Put a module in ``blamethrower/analyzers/<analyzer>.py`` with an
``analyze(bugfile)`` method.  The parameter is a file object that contains the
output of the static analysis tool.  It should return an iterator of
``blamethrower.Analyne`` namedtuples containing the filename, line number,  bug
type, and bug severity (``high``, ``med``, or ``low``).  Set the author to
``None``.

Add a global constant called ``HELP`` to ``<analyzer>.py`` giving a short,
one-line description of the analyzer and how to generate output.

If your analyzer needs user input, add an ``OPTIONS`` dict to ``<analyzer>.py``
that maps option names to short help text.  The ``analyze()`` method will be
called with keyword args for any of these options given on the command line.

Run the analyzer on a modestly-sized real project, bzip2-compress the output
and save it in ``test/analyzers/<project>.<analyzer>.txt.bz2``.  Make sure the
project uses the MIT, BSD, or public domain license if the analyzer output
includes any code.

Determine the correct ``--rawdata`` output (tab-separated ``Analyne`` fields)
for your analyzer; you can either compute this independently, or run it through
``blamethrower --rawdata`` and verify it by hand (remove the header!).
Bzip2-compress it and save it in
``test/analyzers/<project>.<analyzer>.tsv.bz2``.  Add a test to
``test/analyzers/test_analyzers.py``.

Add the module name to the ``__all__`` list in
``blamethrower/analyzers/__init__.py``.

If the analyzer output needs massaging, put a script in ``bin/<analyzer>.sh``
to help people out.

Adding a New Repo Type
~~~~~~~~~~~~~~~~~~~~~~
If the repo is called ``<repo>`` (e.g., ``svn``, ``bzr``), create a module
named ``blamethrower/reporeaders/<repo>.py`` with a ``read(blamefile)`` method.
The method takes in a file object that contains the output of the repository's
annotate command.  It returns an iterable of ``(filename,  list(authors))``
pairs, one for each file in the repository.  ``authorlist[0]`` should be
``None``, and ``authorlist[i]`` is the author of line ``i`` in that file.

Add a global constant called ``HELP`` to ``<repo>.py`` giving a short, one-line
description of the repo type and how to generate output.

If your reporeader needs user input, add an ``OPTIONS`` dict to ``<repo>.py``
that maps option names to short help text.  The ``read()`` method will be
called with keyword args for any options given on the command line.

Run the repo blame tool on a modestly-sized real project, bzip2-compress the
output and save it in ``test/reporeaders/<project>.<repo>.txt.bz2``.  Make sure
the project uses the MIT, BSD, or public domain license if the blame output
includes any code.

Determine the correct ``--rawdata`` output (tab-separated ``Analyne`` fields)
for your repo reader; you can either compute this independently, or run it
through ``blamethrower --rawdata`` and verify it by hand (remove the header!).
Bzip2-compress it and save it in ``test/reporeaders/<project>.<repo>.tsv.bz2``.
Add a test to ``test/reporeaders/test_reporeaders.py``.

Add the module name to the ``__all__`` list in
``blamethrower/reporeaders/__init__.py``.

If the blame output needs massaging, put a script in ``bin/<repo>-blame.sh`` to
help people out.

.. footer:: Copyright (C) 2012 by John Kleint.  BlameThrower is free software,
  licensed under the `MIT license <http://opensource.org/licenses/MIT>`_.

