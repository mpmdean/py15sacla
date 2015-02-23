#!/usr/bin/env python


from py15sacla.hdfselection import HDFSelection


class CCDFrames(object):

    """Numerical operations on a series of detector images in HDF file.

    selection    -- HDFSelection that contains the selected image arrays.

    Configuration:

    cnormalize   -- flag for converting detector values to photon counts,
                    by default True.
    """

    cnormalize = True


    def __init__(self, src):
        """Initialize new CCDFrames object.

        src  -- HDF source for the detector images.  Accepted types are
                HDFSelection, h5py.Group or a string of the HDF file.
                This is used to assign the selection attribute.
        """
        self.selection = HDFSelection(src, "detector_data$")
        return

# End of class CCDFrames
