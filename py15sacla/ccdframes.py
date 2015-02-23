#!/usr/bin/env python


from py15sacla.hdfselection import HDFSelection


class CCDFrames(object):

    """Numerical operations on a series of detector images in HDF file.

    selection    -- HDFSelection that contains the selected image arrays.

    Configuration:

    cSi_gap      -- silicon band gap in eV (3.65)
    cnormalize   -- flag for converting detector values to photon counts,
                    by default True.
    """

    cSi_gap = 3.65
    cnormalize = True


    def __init__(self, src):
        """Initialize new CCDFrames object.

        src  -- HDF source for the detector images.  Accepted types are
                HDFSelection, h5py.Group or a string of the HDF file.
                This is used to assign the selection attribute.
        """
        self.selection = HDFSelection(src, "detector_data$")
        return


    def getFrameConfig(self, detector_data):
        """Read photon energy and absolute gain for a detector_data dataset.

        detector_data    -- h5py.Dataset named "detector_data".  Configuration
                            will be looked up in the parent groups of the same
                            same run.

        Return dictionary with the following keys:
        ('absolute_gain', 'photon_energy_in_eV', 'e_per_ph', 'tophotons')
        """
        assert detector_data.name.endswith('/detector_data')
        rv = {}
        dsgain = detector_data.parent.parent['detector_info/absolute_gain']
        rv['absolute_gain'] = dsgain[0]
        grun = detector_data.parent.parent.parent
        dsphe = grun['run_info/sacla_config/photon_energy_in_eV']
        rv['photon_energy_in_eV'] = dsphe.value
        rv['e_per_ph'] = (rv['photon_energy_in_eV'] /
                (self.cSi_gap * rv['absolute_gain']))
        rv['tophotons'] = 1.0 / rv['e_per_ph']
        return rv

# End of class CCDFrames
