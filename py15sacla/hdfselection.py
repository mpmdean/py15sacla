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
        allnames = []
        already_datasets = False
        if isinstance(src, HDFSelection):
            self.hdffile = src.hdffile
            allnames[:] = src.datanames
            already_datasets = True
        elif isinstance(src, basestring):
            self.hdffile = h5py.File(src)
            self.hdffile.visit(allnames.append)
        elif isinstance(src, h5py.Group):
            self.hdffile = src.file
            src.visit(allnames.append)
        else:
            raise ValueError("Unsupported selection source {0!r}".format(src))
        mp = MultiPattern(pattern)
        dnms = [n for n in allnames if mp.match(n) and
                already_datasets or isinstance(self.hdffile[n], h5py.Dataset)]
        self.datanames = numpy.char.array(dnms)
        return
