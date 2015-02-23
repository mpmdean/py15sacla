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
