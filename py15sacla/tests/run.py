#!/usr/bin/env python

"""Convenience module for executing all unit tests with

python -m py15sacla.tests.run
"""


if __name__ == '__main__':
    import sys
    from py15sacla.tests import test
    # produce zero exit code for a successful test
    sys.exit(not test().wasSuccessful())

# End of file
