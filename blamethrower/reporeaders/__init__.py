# Copyright 2012 John Kleint
# This is free software, licensed under the MIT License; see LICENSE.txt.

"""BlameThrower modules for reading the output of version control system
"blame" (or "annotate") commands."""

__all__ = ['git', 'hg']

if __debug__:
    def _check_reporeader_output(files_authors):
        """Validate the output from a reporeader `analyze` function and pass it through."""
        for filename, authorlist in files_authors:
            assert filename
            assert authorlist and authorlist[0] is None
            assert not any(author is None for author in authorlist[1:])
            yield filename, authorlist
else:
    # Yes, I timed it and this really is faster, even with -O.
    def _check_reporeader_output(files_authors):
        return files_authors
