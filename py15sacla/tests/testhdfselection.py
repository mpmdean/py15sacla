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
    def test_copy(self):
        """check HDFSelection.copy()
        """
        dupl = self.selection.copy()
        self.assertFalse(dupl is self.selection)
        self.assertFalse(dupl._datanames is self.selection._datanames)
        self.assertEqual(self.selection, dupl)
        self.assertTrue(isinstance(dupl, HDFSelection))
        return

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
        hse127 = hse[1:3] | hse[7:8]
        self.assertEqual(hse127.names, hse[idcs_127].names)
        self.assertEqual(hse127.names, hse[idcs_127.tolist()].names)
        return

#   def test___or__(self):
#       """check HDFSelection.__or__()
#       """
#       return
#
#   def test___ior__(self):
#       """check HDFSelection.__ior__()
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
#
#   def test___eq__(self):
#       """check HDFSelection.__eq__()
#       """
#       return
#
#   def test___neq__(self):
#       """check HDFSelection.__neq__()
#       """
#       return not (self == other)
#
#   def test___ge__(self):
#       """check HDFSelection.__ge__()
#       """
#       return
#
#   def test___gt__(self):
#       """check HDFSelection.__gt__()
#       """
#       return
#
#   def test___le__(self):
#       """check HDFSelection.__le__()
#       """
#       return
#
#   def test___lt__(self):
#       """check HDFSelection.__lt__()
#       """
#       return


    def test___contains__(self):
        """check HDFSelection.__contains__()
        """
        sall = self.selection
        sdd = sall.filter('detector_data')
        sth = sall.filter('spectrometer_theta_position')
        self.failUnless(sdd[0] in sall)
        self.failUnless(sth[-1] in sall)
        self.assertFalse(sth[-1] in sdd)
        self.assertFalse(sdd[3] in sth)
        self.assertFalse(sdd[3] in sth)
        self.assertFalse(sall[-1] in sth)
        self.assertTrue(all(ds in sall for ds in sall))
        return

# End of class TestHDFSelection

if __name__ == '__main__':
    unittest.main()

# End of file
