#!/usr/bin/env python

"""Unit tests for py15sacla.hdfselection
"""

import unittest
import numpy
import h5py

from py15sacla.tests.testutils import datafile, hdfdatafile
from py15sacla.ccdframes import CCDFrames

##############################################################################
class TestCCDFrames(unittest.TestCase):

    def setUp(self):
        self.filename = hdfdatafile('265565-01.h5')
        self.ccds = CCDFrames(self.filename)
        return


    def tearDown(self):
        return


    def test___init__(self):
        """check CCDFrames.__init__()
        """
        return


    def test_getFrameConfig(self):
        """check CCDFrames.getFrameConfig()
        """
        cfg = self.ccds.getFrameConfig(self.ccds.selection[0])
        return


# End of class TestCCDFrames

if __name__ == '__main__':
    unittest.main()

# End of file
