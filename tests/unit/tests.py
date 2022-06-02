import unittest
from tests.unit.run_executables import RunExecutables


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(RunExecutables),
    ])
    return suite
