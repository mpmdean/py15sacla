#!/usr/bin/env python

'''Shared utility functions.
'''

SILICON_GAP = 3.65

def eqbinhistogram(a, bins=10, range=None):
    '''Calculate histogram over uniformly spaced bins.
    This uses numpy.bincount which is significantly faster than histogram.

    a    -- input array of arbitrary dimensions.  Histogram is computed
            over flattened array.
    bins -- number of equal-width bins, by default 10.
    range -- an optional tuple of (lobound, hibound) range for the bins.
            Values outside the range are ignored.  When not provided,
            use (a.min(), a.max()).

    Return a tuple of (counts, bin_edges).
    '''
    import numpy
    a = numpy.asarray(a)
    if range is not None:
        lo, hi = map(float, range)
        a1 = a[numpy.logical_and(lo <= a, a <= hi)]
    else:
        lo, hi = a.min(), a.max()
        a1 = a.reshape(-1)
    # Ensure (a1 - lo) is cast as numpy.dtype(float)
    loarray = numpy.array([lo], dtype=float)
    a2 = (a1 - loarray) * (bins / (hi - lo))
    counts = numpy.bincount(a2.astype(int), minlength=bins)
    if len(counts) > bins:
        counts[-2:-1] += counts[-1:]
        counts = counts[:-1]
    assert len(counts) == bins
    bin_edges = numpy.linspace(lo, hi, bins + 1)
    return (counts, bin_edges)


def getDetectorConfig(src):
    """Read photon energy and absolute gain relative to an HDF node.

    src  -- Group or Dataset in a SACLA HDF file hierarchy

    Return dictionary with the following keys:
    ('absolute_gain', 'photon_energy_in_eV', 'e_per_ph', 'tophotons',
     'run_number')
    """
    # upper lookup when src is under some run_N group
    if src.name.startswith('/run_'):
        run_name = src.name.split('/', 2)[1]
        run_number = int(run_name.split('_', 1)[1])
    # use the first run in the file otherwise
    else:
        run_number = src.file['file_info/run_number_list'][0]
        run_name = 'run_{}'.format(run_number)
    # group for the selected run_N
    grun = src.file[run_name]
    # collect configuration data
    rv = {'run_number' : run_number}
    dsgain = grun['detector_2d_1/detector_info/absolute_gain']
    rv['absolute_gain'] = dsgain.value
    dsphe = grun['run_info/sacla_config/photon_energy_in_eV']
    rv['photon_energy_in_eV'] = dsphe.value
    rv['e_per_ph'] = (rv['photon_energy_in_eV'] /
            (SILICON_GAP * rv['absolute_gain']))
    rv['tophotons'] = 1.0 / rv['e_per_ph']
    return rv


def getHDFDataset(src, pattern):
    '''Find h5py.Dataset object matching the pattern.

    src  -- source node for searching for the data.  Accepted types
            HDF5 Group or a string, which is used to open an h5py.File.
    pattern  -- string pattern for matching dataset names.  Must match
            a unique dataset name under the src hierarchy.

    Return an h5py.Dataset object.
    '''
    from py15sacla.hdfselection import HDFSelection
    sel = HDFSelection(src, pattern)
    if len(sel) == 0:
        emsg = "pattern {0!r} does not match anything".format(pattern)
        raise ValueError(emsg)
    elif len(sel) > 1:
        emsg = "pattern {0!r} matches multiple datasets".format(pattern)
        raise ValueError(emsg)
    return sel[0]


def getHDFArray(src, pattern):
    '''Return HDF data matching the pattern as NumPy array.

    src  -- source node for searching for the data.  Accepted types
            HDF5 Group or a string, which is used to open an h5py.File.
    pattern  -- string pattern for matching dataset names.  Must match
            a unique dataset name under the src hierarchy.

    Return NumPy array.
    '''
    return getHDFDataset(src, pattern).value


def unique_ordered(a):
    "Return unique values in array a in the order of appearance."
    import pandas
    return pandas.unique(a)

ordered_unique = unique_ordered


def multiplicities(a):
    "Return multiplicities of unique values in array a."
    import numpy
    import collections
    a = numpy.asarray(a)
    cnts = collections.OrderedDict()
    for x in a.flat:
        cnts[x] = cnts.get(x, 0) + 1
    return numpy.array(cnts.values())


def findfiles(patterns=(), path=None):
    '''Return filenames that match all specified patterns.

    patterns -- a list of string patterns that must all match in the
                the returned files.  Can be also a single string with
                patterns separated by whitespace characters.
    path     -- optional list of directories to be searched instead
                of the current directory.  Can be also a string which
                is taken as a single directory path.

    Pattern syntax and examples:

    ^start   -- match "start" only at the beginning of the string
    end$     -- match "end" only at the end of string
    <7>      -- match number 7 preceded by any number of leading zeros
    <1-34>   -- match an integer range.  The matched number may have
                one or more leading zeros
    <7->     -- match an integer greater or equal 7 allowing leading zeros
    <->      -- match any integer

    Return a list of matching filenames.
    '''
    import os.path
    from py15sacla.multipattern import MultiPattern
    from IPython.utils.text import SList
    if isinstance(path, basestring):
        path = [path]
    mp = MultiPattern(patterns)
    allpaths = ['.'] if path is None else path
    rv = SList()
    for d in unique_everseen(allpaths):
        if not os.path.isdir(d):  continue
        dirfiles = os.listdir(d)
        dirfiles.sort(key=sortKeyNumericString)
        # filter matching names first, this does not need any disk access
        files = filter(mp.match, dirfiles)
        files = [os.path.normpath(os.path.join(d, f)) for f in files]
        # filter out any directories
        files = filter(os.path.isfile, files)
        rv += files
    return rv


def unique_everseen(iterable, key=None):
    """Return a generator to unique ordered elements in an iterable.

    iterable -- an iterable object
    key      -- function that returns key for finding unique items.
                Use the item value when None.

    unique_everseen('AAAABBBCCDAABBB') --> A B C D
    unique_everseen('ABBCcAD', str.lower) --> A B C D
    """
    seen = set()
    for element in iterable:
        k = element if key is None else key(element)
        if k not in seen:
            seen.add(k)
            yield element
    pass


def sortKeyNumericString(s):
    """This function can be used as a key argument for sort to order
    string items in numeric, rather than alphabetic order.

    s    -- string entry

    Return a key for comparison in sorting.  The string s is split at
    integer segments that are then converted to integers.  Signs, decimal
    points and exponents in s are ignored.
    """
    if not hasattr(sortKeyNumericString, 'rxdigits'):
        import re
        sortKeyNumericString.rxdigits = re.compile(r'(\d+)')
    rv = sortKeyNumericString.rxdigits.split(s)
    rv[1::2] = map(int, rv[1::2])
    return rv
