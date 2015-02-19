#!/usr/bin/env python

"""Unit tests for py15sacla.hdfselection
"""

import unittest
import numpy
import h5py

from py15sacla.tests.testutils import datafile, hdfdatafile
from py15sacla.hdfselection import HDFSelection

##############################################################################
class TestHDFSelection(unittest.TestCase):

    def setUp(self):
        self.filename = hdfdatafile('265565-01.h5')
        self.selection = HDFSelection(self.filename)
        return


    def tearDown(self):
        self.selection.hdffile.close()
        return

#   def test___init__(self):
#       """check HDFSelection.__init__()
#       """
#       return
#
#   def test___str__(self):
#       """check HDFSelection.__str__()
#       """
#       return
#
#   def test_filter(self):
#       """check HDFSelection.filter()
#       """
#       return
#
#   def test___iter__(self):
#       """check HDFSelection.__iter__()
#       """
#       return
#
#   def test_copy(self):
#       """check HDFSelection.copy()
#       """
#       return
#
#   def test_min(self):
#       """check HDFSelection.min()
#       """
#       return
#
#   def test_max(self):
#       """check HDFSelection.max()
#       """
#       return
#
#   def test_sum(self):
#       """check HDFSelection.sum()
#       """
#       return


    def test___len__(self):
        """check HDFSelection.__len__()
        """
        self.assertEqual(202, len(self.selection))
        return


    def test___getitem__(self):
        """check HDFSelection.__getitem__()
        """
        hse = self.selection
        self.failUnless(isinstance(hse[0], h5py.Dataset))
        self.failUnless(isinstance(hse[:1], HDFSelection))
        self.assertEqual(sorted(hse.names), hse[::-1].names)
        # boolean array
        flag_all = numpy.ones(len(hse), dtype=bool)
        self.assertEqual(hse.names, hse[flag_all].names)
        flag_2nd = numpy.zeros(len(hse), dtype=bool)
        flag_2nd[1] = True
        self.assertEqual(hse[1:2].names, hse[flag_2nd].names)
        # integer array
        idcs_rev = numpy.arange(len(hse))[::-1]
        self.assertEqual(hse.names, hse[idcs_rev].names)
        idcs_127 = numpy.array([1, 2, 7])
        hse127 = hse[1:3] + hse[7:8]
        self.assertEqual(hse127.names, hse[idcs_127].names)
        self.assertEqual(hse127.names, hse[idcs_127.tolist()].names)
        return

#   def test___add__(self):
#       """check HDFSelection.__add__()
#       """
#       return
#
#   def test___iadd__(self):
#       """check HDFSelection.__iadd__()
#       """
#       return
#
#   def test___sub__(self):
#       """check HDFSelection.__sub__()
#       """
#       return
#
#   def test___isub__(self):
#       """check HDFSelection.__isub__()
#       """
#       return

# End of class TestHDFSelection

if __name__ == '__main__':
    unittest.main()

# End of file
