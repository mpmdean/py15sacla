#!/usr/bin/env python


import numpy
from py15sacla.hdfselection import HDFSelection


class CCDFrames(object):

    """Numerical operations on a series of detector images in HDF file.

    selection    -- HDFSelection that contains the selected image arrays.

    Configuration:

    cnormalize   -- flag for converting detector values to photon counts,
                    by default True.
    croislice    -- a tuple of slices that delineate region of interest in
                    the image arrays.  Empty tuple stands for the whole image.
    cbackground  -- 2D array of background values to be subtracted from the
                    region of interest.
    cthreshold   -- tuple of (lobound, hibound) filter for background
                    subtracted arrays.  Thereshold is not applied for the
                    bounds set to None.
    chistbins    -- tuple of (lobound, hibound, bincount) values for
                    configuring histogram bins.
    """

    cnormalize = True
    croislice = ()
    cbackground = 0
    cthreshold = (None, None)
    chistbins = ()

    def __init__(self, src):
        """Initialize new CCDFrames object.

        src  -- HDF source for the detector images.  Accepted types are
                HDFSelection, h5py.Group or a string of the HDF file.
                This is used to assign the selection attribute.
        """
        self.selection = HDFSelection(src, "detector_data$")
        return


    def groupby(self, keys):
        """Return a list of CCDFrames groupped by unique keys.

        keys -- iterable collection of the same size as this selection.
                The objects inside must be usable as dictionary keys.

        Return a list of CCDFrames objects.
        """
        rv = [kccd[1] for kccd in self.groupbyitems(keys)]
        return rv


    def groupbyitems(self, keys):
        """Return a list of CCDFrames groupped by unique keys.

        When cbackground is of a CCDFrames type, it is split accordingly.

        keys -- iterable collection of the same size as this selection.
                The objects inside must be usable as dictionary keys.

        Return a list of (unique_key, CCDFrames) pairs.
        """
        import copy
        rv = []
        for k, sel in self.selection.groupbyitems(keys):
            selccd = copy.copy(self)
            selccd.selection = sel
            rv.append((k, selccd))
        if isinstance(self.cbackground, CCDFrames):
            ccdlist = [ccd for k, ccd in rv]
            bggroups = self.cbackground.groupby(keys)
            for ccd, bg in zip(ccdlist, bggroups):
                ccd.setBackground(bg)
        return rv


    def setROI(self, roislice):
        """Set region of interest used for image processing.

        roislice -- a tuple of slice objects for row and column indices,
                    for example: numpy.s_[:100,:100].

        No return value.  Assign croislice.
        """
        self.croislice = roislice
        return


    def setBackground(self, background):
        """Set normalized background image to be subtracted from the data.

        background   -- numpy array of photon counts or CCDFrames that
                        correspond to a series of background images.
                        Set to 0 to turn-off background subtraction.

        No return value.  Assign cbackground.
        """
        import copy
        if background is self:
            background = copy.copy(self)
            background.selection = self.selection.copy()
        self.cbackground = background
        return


    def setThreshold(self, lo, hi):
        """Set threshold window for background-subtracted values.

        Values in normalized background-subtracted images that are outside
        of threshold range are reset to 0.

        lo   -- lower threshold bound.  Maps to -inf if None.
        hi   -- upper threshold bound.  Maps to +inf if None.

        No return value.  Assing cthreshold.
        """
        self.cthreshold = (lo, hi)
        return


    def setHistBins(self, lo, hi, bins):
        """Configure bins for the histogram of the processed image arrays.

        lo   -- minimum value included in the histogram.
        hi   -- maximum value included in the histogram
        bins -- number of histogram bins between lo and hi

        No return value.  Assing chistbins.
        """
        self.chistbins = (lo, hi, bins)
        return


    def generate(self, start=0):
        """Return iterator to the processed image data.

        start    -- start generating from that data frame if nonzero.

        The iterator returns normalized, background-subtracted, thresholded
        arrays.
        """
        import itertools
        from py15sacla.utils import getDetectorConfig
        # create iterator that returns background arrays
        ibg = itertools.repeat(self.cbackground)
        if isinstance(self.cbackground, CCDFrames):
            nbg = len(self.cbackground.selection)
            if nbg != len(self.selection):
                raise ValueError("Incompatible length of background frames.")
            ibg = self.cbackground.generate()
        idd = iter(self.selection)
        if start:
            next(itertools.islice(ibg, start, start), None)
            next(itertools.islice(idd, start, start), None)
        for dd in idd:
            # ROI
            rv = dd[self.croislice]
            # convert to photon counts if requested
            cfg = getDetectorConfig(dd)
            if self.cnormalize:
                rv *= cfg['tophotons']
            # background
            bg = ibg.next()
            if numpy.shape(bg) == dd.shape:
                bg = bg[self.croislice]
            rv -= bg
            # threshold
            lo, hi = self.cthreshold
            if lo is not None:
                rv[rv < lo] = 0
            if hi is not None:
                rv[rv > hi] = 0
            yield rv
        pass


    def toarray(self, index):
        """Return NumPy array of processed image data.

        index    -- integer, slice, array of boolean flags, or
                    other index type accepted in numpy arrays.

        Return 2D array for scalar index.  Return 3D array if
        index is a range.
        """
        from py15sacla.utils import unique_ordered
        nsel = len(self.selection)
        indices = numpy.arange(nsel)[index]
        indices = unique_ordered(indices.reshape(-1))
        rv = numpy.empty(0, dtype=float)
        for i, idx in enumerate(indices):
            aa = self.generate(start=idx).next()
            if not rv.size:
                rv.resize(len(indices), *aa.shape)
            rv[i] = aa
        if len(rv) == 1:
            rv = rv.squeeze(0)
        return rv


    def compress(self, keys, method, bgmap=None):
        '''Compress processed image frames at the repeated keys.

        keys     -- iterable collection of the same size as the selection.
                    The key values must be usable as dictionary keys.
        method   -- string from ('mean', 'sum', 'total') or a callable object.
                    When string, use that CCDFrames method to compress
                    equivalent frames.  Otherwise use method(ccdgroup) to
                    produce elements of the compressed arrays.
        bgmap    -- dictionary that maps each key to a background array.
                    May be also a tuple of (keyvalues, bgarrays) which is
                    converted to a dictionary.

        Return a tuple of (unique_keys, compressed_images).
        '''
        from py15sacla.utils import unique_ordered
        fzip = method
        if isinstance(method, basestring):
            assert method in 'mean sum total'.split()
            fzip = getattr(CCDFrames, method)
        ccdgroups = self.groupby(keys)
        if bgmap is not None:
            if isinstance(bgmap, tuple) and 2 == len(bgmap):
                bgmap = dict(zip(*bgmap))
            for ccd, x in zip(ccdgroups, unique_ordered(keys)):
                ccd.setBackground(bgmap[x])
        ukeys = unique_ordered(keys)
        zipped = numpy.array([fzip(ccd) for ccd in ccdgroups])
        return (ukeys, zipped)


    def sum(self):
        "Return sum of the processed image data as a 2D array."
        return sum(self.generate())


    def total(self):
        "Return sum of all values from the processed image frames."
        psums = map(lambda aa: aa.sum(), self.generate())
        return sum(psums)


    def mean(self):
        """Return average corrected frame as a 2D array.
        """
        return self.sum() / max(1, len(self.selection))


    def atotal(self):
        "Return array of totals from all pixels per each processed frame."
        psums = map(lambda aa: aa.sum(), self.generate())
        return numpy.array(psums)


    def amin(self):
        """Return array of minimum values per each processed frame.
        """
        rv = numpy.array([aa.min() for aa in self.generate()])
        return rv


    def amax(self):
        """Return array of maximum values per each processed frame.
        """
        rv = numpy.array([aa.max() for aa in self.generate()])
        return rv


    def ahistogram(self):
        """Get histogram counts per each processed CCD frame as a 2D array.

        Use setHistBins to configure histogram bins.  Bin edges and centers
        are available in self.hedges and self.hcenters.

        Return a 2D array of histogram counts per each frame.
        """
        import functools
        from py15sacla.utils import eqbinhistogram
        self._ensureHistBinsExist()
        lo, hi, bins = self.chistbins
        fnc = functools.partial(eqbinhistogram, bins=bins, range=(lo, hi))
        histcounts = map(fnc, self.generate())
        rv = numpy.array([c for c, e in histcounts])
        return rv


    def histogram(self):
        """Return histogram counts of all processed frames.

        Use setHistBins to configure histogram bins.  Bin edges and centers
        are available in self.hedges and self.hcenters.

        Return a simple array of bin counts.
        """
        rv = self.ahistogram().sum(axis=0)
        return rv

    # properties

    @property
    def hdffile(self):
        "Same as self.selection.hdffile."
        return self.selection.hdffile


    @property
    def hcenters(self):
        "Array of center positions of the histogram bins."
        e = self.hedges
        return 0.5 * (e[:-1] + e[1:])


    @property
    def hedges(self):
        "Histogram bin edges as numpy array."
        self._ensureHistBinsExist()
        lo, hi, bins = self.chistbins
        return numpy.linspace(lo, hi, bins + 1)

    # helper methods

    def _ensureHistBinsExist(self):
        """Set default histogram bins if they were not yet configured.
        """
        if not self.chistbins:
            self.setHistBins(min(self.amin()), max(self.amax()), 50)
        return

# End of class CCDFrames
