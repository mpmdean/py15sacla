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
        pattern  -- optional string pattern for matching dataset names.
                By default an empty string that matches everything.
        mode -- Python mode used for opening the HDF5 file, by default 'r'.
                Used only when src is a string.
        '''
        if mode is not None and not isinstance(src, basestring):
            raise ValueError("mode is valid only when src is a filename.")
        self._datanames = []
        collect_datanames = lambda n, v: (isinstance(v, h5py.Dataset) and
                self._datanames.append('/' + n.lstrip('/')) or None)
        if isinstance(src, HDFSelection):
            self.hdffile = src.hdffile
            self._datanames[:] = src._datanames
        elif isinstance(src, basestring):
            m = 'r' if mode is None else mode
            self.hdffile = h5py.File(src, mode=m)
            self.hdffile.visititems(collect_datanames)
            self._datanames.sort()
        elif isinstance(src, h5py.Group):
            self.hdffile = src.file
            src.visititems(collect_datanames)
            self._datanames.sort()
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


    def filter(self, fnc):
        """Return sub-selection where filter function evaluates to True.

        fnc  -- function or callable object, which is evaluate with each
                dataset in this selection.

        Return new HDFSelection object.
        """
        if not callable(fnc):
            raise TypeError("fnc must be string or a callable object.")
        hdfsel = self.copy()
        hdfsel._datanames = [n for n in self._datanames
                if fnc(self.hdffile[n])]
        return hdfsel


    def groupby(self, keys):
        """Split this selection to subsets groupped by unique keys.

        keys -- iterable collection of the same size as this selection.
                The objects inside must be usable as dictionary keys.

        Return a list of HDFSelection objects.
        """
        rv = [kse[1] for kse in self.groupbyitems(keys)]
        return rv


    def groupbyitems(self, keys):
        """Split this selection to subsets groupped by unique keys.

        keys -- iterable collection of the same size as this selection.
                The objects inside must be usable as dictionary keys.

        Return a list of (unique_key, HDFSelection) pairs.
        """
        from collections import OrderedDict
        groups = OrderedDict()
        cnt = 0
        for i, k in enumerate(keys):
            if not k in groups:
                groups[k] = []
            groups[k].append(i)
            cnt += 1
        if cnt != len(self):
            emsg = "groupby keys must be of the compatible length."
            raise ValueError(emsg)
        rv = [(k, self[gi]) for k, gi in groups.iteritems()]
        return rv


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

    # Support collection-like operations

    def __len__(self):
        return len(self._datanames)


    def __getitem__(self, key):
        """Get dataset or a slice from this selection.

        key  -- bracket index.  Return Dataset when integer.
                Return HDFSelection, when slice or NumPy array of indices
                or boolean flags.  When string, return HDFSelection with
                matching dataset names.

        Return Dataset or HDFSelection.
        """
        if isinstance(key, int):
            return self.hdffile[self._datanames[key]]
        if isinstance(key, basestring):
            mp = MultiPattern(key)
            dnms = [n for n in self._datanames if mp.match(n)]
        elif isinstance(key, slice):
            dnms = self._datanames[key]
        else:
            indices = numpy.arange(len(self))[key]
            dnms = [self._datanames[i] for i in indices]
        dnms.sort()
        rv = self.copy()
        rv._datanames = dnms
        return rv

    # operators for union and difference of the selections

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

    # Comparison operators:

    def __eq__(self, other):
        rv = (self.hdffile == other.hdffile and
                self._datanames == other._datanames)
        return rv


    def __neq__(self, other):
        return not (self == other)


    def __ge__(self, other):
        rv = (self.hdffile == other.hdffile and
                set(self._datanames) >= set(other._datanames))
        return rv


    def __gt__(self, other):
        rv = (self.hdffile == other.hdffile and
                set(self._datanames) > set(other._datanames))
        return rv


    def __le__(self, other):
        rv = (self.hdffile == other.hdffile and
                set(self._datanames) <= set(other._datanames))
        return rv


    def __lt__(self, other):
        rv = (self.hdffile == other.hdffile and
                set(self._datanames) < set(other._datanames))
        return rv


    def __contains__(self, x):
        "True if x is a Dataset object in this selection."
        import bisect
        rv = (isinstance(x, h5py.Dataset) and x.file == self.hdffile)
        if rv:
            i = bisect.bisect_left(self._datanames, x.name)
            rv = (i < len(self._datanames) and self._datanames[i] == x.name)
        return rv

    # Internal helper functions

    def __checkOperationArgument(self, other):
        "Check validity of the argument for addition or subtraction."
        if not isinstance(other, HDFSelection):
            emsg = 'The object must be of HDFSelection type.'
            raise TypeError(emsg)
        if self.hdffile != other.hdffile:
            raise ValueError('Selections must refer to the same hdffile.')
        return
