import unittest
import ghdecoy


class TestCalendarFunctions(unittest.TestCase):

    def test_get_calendar(self):
        cal = ghdecoy.get_calendar('tickelton')
        self.assertEqual(cal[0].find('<svg'), 0)

if __name__ == '__main__':
    unittest.main()
