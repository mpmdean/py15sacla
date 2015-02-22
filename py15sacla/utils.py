#!/usr/bin/env python

'''Shared utility functions.
'''


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
