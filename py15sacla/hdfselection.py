#!/usr/bin/env python


import numpy
import h5py
from py15sacla.multipattern import MultiPattern


class HDFSelection(object):

    hdffile = None
    _datanames = None

    def __init__(self, src, pattern='', mode=None):
        '''Initialize new HDFSelection

        src  -- source node for selecting HDF5 datasets.  Accepted types
                are HDFSelection, HDF5 Group or a string, which is used
                to open an h5py.File.
        pattern  -- optional string pattern for filtering _datanames.
                By default an empty string that matches everything.
        mode -- Python mode used for opening the HDF5 file, by default 'r'.
                Used only when src is a string.
        '''
        if mode is not None and not isinstance(src, basestring):
            raise ValueError("mode is valid only when src is a filename.")
        self._datanames = []
        collect_datanames = lambda n, v: (isinstance(v, h5py.Dataset) and
                self._datanames.append(n) or None)
        if isinstance(src, HDFSelection):
            self.hdffile = src.hdffile
            self._datanames[:] = src._datanames
        elif isinstance(src, basestring):
            m = 'r' if mode is None else mode
            self.hdffile = h5py.File(src, mode=m)
            self.hdffile.visititems(collect_datanames)
        elif isinstance(src, h5py.Group):
            self.hdffile = src.file
            src.visititems(collect_datanames)
        else:
            raise TypeError("Unsupported selection source {0!r}.".format(src))
        if pattern:
            mp = MultiPattern(pattern)
            self._datanames = [n for n in self._datanames if mp.match(n)]
        return
