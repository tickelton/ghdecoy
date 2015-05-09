import unittest
import ghdecoy

class GHDecoyOnlineTests(unittest.TestCase):
    """Unit tests form 'ghdecoy.py"""

    def test_get_calendar(self):
        cal = ghdecoy.get_calendar('tickelton')
        self.assertEqual(cal[0].find('<svg'), 0)

#class GHDecoyOfflineTests(unittest.TestCase):


if __name__ == '__main__':
    unittest.main()