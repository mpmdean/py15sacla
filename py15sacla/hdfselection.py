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


    def __str__(self):
        '''String representation of this HDF selection.
        '''
        import pprint
        dfmt = pprint.pformat(self._datanames)
        rv = "HDFSelection({})".format(dfmt)
        return rv


    def filter(self, pattern):
        """Filter to records where pattern matches are evaluates to True.

        pattern  -- either a string that is matched to the HDF names
                    or a callable object, which is evaluated with a
                    dataset argument.

        Return new HDFSelection object.
        """
        if isinstance(pattern, basestring):
            return HDFSelection(self, pattern)
        if callable(pattern):
            hdfsel = self.copy()
            hdfsel._datanames = [n for n in self._datanames
                    if pattern(self.hdffile[n])]
            return hdfsel
        raise TypeError("pattern must be string or a callable object.")


    def __iter__(self):
        """Return iterator over the selected datasets.
        """
        for n in self._datanames:
            yield self.hdffile[n]
        pass


    def copy(self):
        "Return a copy of this selection."
        return HDFSelection(self)

    # Properties:

    @property
    def names(self):
        "Return list of names of the HDF datasets in the selection."
        return self._datanames[:]

    @property
    def datasets(self):
        "Return list of the selected HDF Dataset objects."
        return list(self)

    # Common dataset operations:

    def min(self, slice=()):
        """Build array of minimum values per each dataset.

        slice    -- optional slice range to be applied on the dataset,
                    e.g., numpy.s_[:50,:50].

        Return NumPy array.
        """
        return numpy.array([numpy.min(ds[slice], axis=axis) for ds in self])


    def max(self, slice=()):
        """Build array of maximum values per each dataset.

        slice    -- optional slice range to be applied on the dataset,
                    e.g., numpy.s_[:50,:50].

        Return NumPy array.
        """
        return numpy.array([numpy.max(ds[slice], axis=axis) for ds in self])


    def sum(self, slice=()):
        '''Return sum of datasets in the selection.

        slice    -- optional slice range to be applied on the dataset,
                    e.g., numpy.s_[0:50:2,0:50:2].

        Return NumPy array.
        '''
        rv = reduce(lambda x, y : x[slice] + y[slice], self)
        rv = numpy.asarray(rv)
        return rv


    def __len__(self):
        return len(self._datanames)


    def __getitem__(self, key):
        if isinstance(key, int):
            return self.hdffile[self._datanames[key]]
        if isinstance(key, slice):
            dnms = self._datanames[key]
        else:
            indices = numpy.arange(len(self))[key]
            dnms = [self._datanames[i] for i in indices]
        dnms.sort()
        rv = self.copy()
        rv._datanames = dnms
        return rv


    def __or__(self, other):
        '''Return a union of this HDFSelection with another.

        other    -- another HDFSelection referring to the same hdffile.

        Return a new HDFSelection object.
        '''
        rv = self.copy()
        rv |= other
        return rv


    def __ior__(self, other):
        '''Extend this HDFSelection with items from the other.

        other    -- another HDFSelection referring to the same hdffile.

        Return self.
        '''
        self.__checkOperationArgument(other)
        self._datanames = sorted(set(self._datanames).union(other._datanames))
        return self


    def __sub__(self, other):
        '''Return new HDFSelection with datasets removed.

        other    -- HDFSelection that is to be removed.  It must refer
                    to the same hdffile.

        Return new HDFSelection.
        '''
        rv = self.copy()
        rv -= other
        return rv


    def __isub__(self, other):
        '''Remove specified items from this selection.

        other    -- HDFSelection that is to be removed.  It must refer
                    to the same hdffile.

        Return self.
        '''
        self.__checkOperationArgument(other)
        dropnames = set(other._datanames)
        self._datanames = [n for n in self._datanames if n not in dropnames]
        return self

    # Internal helper functions

    def __checkOperationArgument(self, other):
        "Check validity of the argument for addition or subtraction."
        if not isinstance(other, HDFSelection):
            emsg = 'The object must be of HDFSelection type.'
            raise TypeError(emsg)
        if self.hdffile != other.hdffile:
            raise ValueError('Selections must refer to the same hdffile.')
        return
