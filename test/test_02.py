import unittest
import sys
import ghdecoy


class TestDryRun(unittest.TestCase):

    def setUp(self):
        sys.argv = ['ghdecoy.ph',
                    '-u', 'tickelton',
                    '-n', 'fill']
        ghdecoy.main()

    def test_dryrun(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
