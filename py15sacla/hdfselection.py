#!/usr/bin/env python


import numpy
import h5py
from py15sacla.multipattern import MultiPattern


class HDFSelection(object):

    hdffile = None
    datanames = None

    def __init__(self, src, pattern=''):
        '''Initialize new HDFSelection

        src  -- source node for selecting HDF5 datasets.  Accepted types
                are HDFSelection, HDF5 Group or a string, which is used
                to open an h5py.File.
        pattern  -- optional string pattern for filtering datanames.
                By default an empty string that matches everything.
        '''
        self.datanames = []
        collect_datanames = lambda n, v: (isinstance(v, h5py.Dataset) and
                self.datanames.append(n) or None)
        if isinstance(src, HDFSelection):
            self.hdffile = src.hdffile
            self.datanames[:] = src.datanames
        elif isinstance(src, basestring):
            self.hdffile = h5py.File(src)
            self.hdffile.visititems(collect_datanames)
        elif isinstance(src, h5py.Group):
            self.hdffile = src.file
            src.visititems(collect_datanames)
        else:
            raise ValueError("Unsupported selection source {0!r}".format(src))
        if pattern:
            mp = MultiPattern(pattern)
            self.datanames = [n for n in self.datanames if mp.match(n)]
        return
