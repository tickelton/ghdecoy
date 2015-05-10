import unittest
import ghdecoy


class GHDecoyOnlineTests(unittest.TestCase):
    """Unit tests for 'ghdecoy.py' that require an internet connection"""

    def test_get_calendar(self):
        cal = ghdecoy.get_calendar('tickelton')
        self.assertEqual(cal[0].find('<svg'), 0)


class GHDecoyOfflineTests(unittest.TestCase):
    """Unit tests for 'ghdecoy.py' that don't require an internet connection"""

    def test_get_factor_for_vals_1_to_4(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 0},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 2},
            {'date': '2015-01-04T12:00:00', 'count': 3},
            {'date': '2015-01-05T12:00:00', 'count': 4},
        ]
        factor = ghdecoy.get_factor(data)
        self.assertEqual(factor, 1)

    def test_get_factor_for_max_val_0(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 0},
        ]
        factor = ghdecoy.get_factor(data)
        self.assertEqual(factor, 1)

    def test_get_factor_for_max_val_5(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 5},
        ]
        factor = ghdecoy.get_factor(data)
        self.assertEqual(factor, 2)

    def test_get_factor_for_max_val_8(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 8},
        ]
        factor = ghdecoy.get_factor(data)
        self.assertEqual(factor, 2)

    def test_get_factor_for_negative_value(self):
        # FIXME: Maybe this should better check for an exception as negative
        #        values should not occur and probably indicate an error
        #        in some earlier piece of code.
        data = [
            {'date': '2015-01-01T12:00:00', 'count': -5},
        ]
        factor = ghdecoy.get_factor(data)
        self.assertEqual(factor, 1)

    def test_cal_scale_5_by_2(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 5},
        ]
        ghdecoy.cal_scale(2, data)
        self.assertEqual(data[0]['count'], 10)

    def test_cal_scale_empty_list(self):
        # TODO: This should probably result in an error/exception.
        data = []
        ghdecoy.cal_scale(2, data)
        self.assertListEqual(data, [])

    def test_cal_scale_negative_value(self):
        # NOTE: There shouldn't be any negative values in the input data of
        #       cal_scale(). Though as this type of error should be caught in
        #       get_factor(), scaling all values regardless of their sign is
        #       the right thing to do for brevity's sake.
        data = [
            {'date': '2015-01-01T12:00:00', 'count': -5},
        ]
        ghdecoy.cal_scale(2, data)
        self.assertEqual(data[0]['count'], -10)

    @unittest.expectedFailure
    def test_parse_args_help(self):
        # FIXME: This should not fail.
        #        The return code on -h/--help should be 0 as this is a valid
        #        flag  and should be able to be used on it's own.
        #        In practice the return code will be 1 as the presence of the
        #        mandatory command (fill/append) is checked before the
        #        individual flags are evaluated.
        with self.assertRaisesRegexp(SystemExit, '^0$'):
            ghdecoy.parse_args(['./ghdecoy.py', '-h'])

if __name__ == '__main__':
    unittest.main()
