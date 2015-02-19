#!/usr/bin/env python

"""Unit tests for py15sacla.hdfselection
"""

import unittest
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
        self.assertEqual(sorted(hse.names), hse[:].names)
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
