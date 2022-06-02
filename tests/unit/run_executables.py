import unittest
from secure_squash_root import run_prog


class RunExecutables(unittest.TestCase):

    def test__run_prog(self):
        run_prog(["dash", "-c", "exit 3"], 3)
