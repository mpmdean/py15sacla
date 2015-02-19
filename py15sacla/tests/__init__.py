#!/usr/bin/env python

"""Unit tests for py15sacla.
"""

def testsuite():
    '''Build a unit tests suite for the diffpy.Structure package.

    Return a unittest.TestSuite object.
    '''
    import unittest
    modulenames = '''
        py15sacla.tests.testhdfselection
    '''.split()
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for mname in modulenames:
        exec ('import %s as mobj' % mname)
        suite.addTests(loader.loadTestsFromModule(mobj))
    return suite


def test():
    '''Execute all unit tests for the diffpy.Structure package.
    Return a unittest TestResult object.
    '''
    import unittest
    suite = testsuite()
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result


# End of file
