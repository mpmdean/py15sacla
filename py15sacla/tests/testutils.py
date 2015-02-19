#!/usr/bin/env python

"""Helper routines for running other unit tests.
"""

# helper functions

def datafile(filename):
    from pkg_resources import resource_filename
    rv = resource_filename(__name__, filename)
    return rv


def hdfdatafile(filename):
    import os
    fn = datafile(filename)
    if not os.path.isfile(fn):
        emsg = filename + " is missing, symlink it to the tests/ directory."
        raise RuntimeError(emsg)
    return fn
