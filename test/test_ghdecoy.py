import unittest
import ghdecoy
import os
import datetime


class GHDecoyOnlineTests(unittest.TestCase):
    """Unit tests for 'ghdecoy.py' that require an internet connection"""

    def test_get_calendar(self):
        cal = ghdecoy.get_calendar('tickelton')
        found_svg = False
        for row in cal:
            if row.find('<svg'):
                found_svg = True
                break
        self.assertTrue(found_svg)


class GHDecoyIOTests(unittest.TestCase):
    """Unit tests for 'ghdecoy.py' that perform disk IO"""

    outfile = "/tmp/ghdecoy.sh"

    def test_create_script(self):
        conf = {
            'lang': 'raw',
            'dryrun': False,
            'wdir': '/tmp',
            'min_days': 1,
            'keep': True,
            'repo': 'decoy',
            'max_shade': 4,
            'user': 'tickelton',
            'action': 'fill'
        }
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 2},
            {'date': '2015-01-03T12:00:00', 'count': 3},
            {'date': '2015-01-04T12:00:00', 'count': 4},
            {'date': '2015-01-05T12:00:00', 'count': 0},
        ]
        template = (
            '#!/bin/bash\n'
            'set -e\n'
            'REPO={0}\n'
            'git init $REPO\n'
            'cd $REPO\n'
            'touch decoy{1}\n'
            'git add decoy{1}\n'
            '{2}\n'
            'git remote add origin git@github.com:{3}/$REPO.git\n'
            'set +e\n'
            'git pull\n'
            'set -e\n'
            'git push -f -u origin master\n'
        )
        result = [
            '#!/bin/bash\n',
            'set -e\n',
            'REPO=decoy\n',
            'git init $REPO\n',
            'cd $REPO\n',
            'touch decoy\n',
            'git add decoy\n',
            'echo 0 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-01T12:00:00 GIT_COMMITTER_DATE=2015-01-01T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 1 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-02T12:00:00 GIT_COMMITTER_DATE=2015-01-02T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 2 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-02T12:00:00 GIT_COMMITTER_DATE=2015-01-02T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 3 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-03T12:00:00 GIT_COMMITTER_DATE=2015-01-03T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 4 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-03T12:00:00 GIT_COMMITTER_DATE=2015-01-03T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 5 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-03T12:00:00 GIT_COMMITTER_DATE=2015-01-03T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 6 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-04T12:00:00 GIT_COMMITTER_DATE=2015-01-04T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 7 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-04T12:00:00 GIT_COMMITTER_DATE=2015-01-04T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 8 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-04T12:00:00 GIT_COMMITTER_DATE=2015-01-04T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 9 > decoy\n',
            'GIT_AUTHOR_DATE=2015-01-04T12:00:00 GIT_COMMITTER_DATE=2015-01-04T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            '\n',
            'git remote add origin git@github.com:tickelton/$REPO.git\n',
            'set +e\n',
            'git pull\n',
            'set -e\n',
            'git push -f -u origin master\n',
        ]

        ghdecoy.create_script(conf, data, template)

        with open(self.outfile, "r") as shfile:
            readback = shfile.readlines()

        self.maxDiff = None
        self.assertListEqual(result, readback)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.outfile)


class GHDecoyMiscTests(unittest.TestCase):
    """Miscellaneous unit tests for 'ghdecoy.py'

    The tests in this class neither require an internet connection nor do the
    create files on disk.
    """

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
        self.assertEqual(factor, 1)

    def test_get_factor_for_max_val_8(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 8},
        ]
        factor = ghdecoy.get_factor(data)
        self.assertEqual(factor, 2)

    def test_get_factor_for_negative_value(self):
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
        data = []
        ghdecoy.cal_scale(2, data)
        self.assertListEqual(data, [])

    def test_cal_scale_negative_value(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': -5},
        ]
        ghdecoy.cal_scale(2, data)
        self.assertEqual(data[0]['count'], -10)

    def test_parse_args_help(self):
        with self.assertRaisesRegexp(SystemExit, '^0$'):
            ghdecoy.parse_args(['./ghdecoy.py', '-h'])

    def test_parse_args_help_long(self):
        with self.assertRaisesRegexp(SystemExit, '^0$'):
            ghdecoy.parse_args(['./ghdecoy.py', '--help'])

    def test_parse_args_version(self):
        with self.assertRaisesRegexp(SystemExit, '^0$'):
            ghdecoy.parse_args(['./ghdecoy.py', '-v'])

    def test_parse_args_version_long(self):
        with self.assertRaisesRegexp(SystemExit, '^0$'):
            ghdecoy.parse_args(['./ghdecoy.py', '--version'])

    def test_parse_args_nocmd(self):
        with self.assertRaisesRegexp(SystemExit, '^1$'):
            ghdecoy.parse_args(['./ghdecoy.py', '-u', 'tickelton'])

    def test_parse_args_invalid_arg(self):
        with self.assertRaisesRegexp(SystemExit, '^1$'):
            ghdecoy.parse_args(['./ghdecoy.py', '-x', 'fill'])

    def test_parse_args_invalid_command(self):
        with self.assertRaisesRegexp(SystemExit, '^1$'):
            ghdecoy.parse_args(['./ghdecoy.py', 'foo'])

    def test_parse_args_invalid_language(self):
        with self.assertRaisesRegexp(SystemExit, '^1$'):
            ghdecoy.parse_args(['./ghdecoy.py', '-l', 'foobar', 'fill'])

    def test_parse_args_invalid_shade(self):
        conf = ghdecoy.parse_args(['./ghdecoy.py', '-p', '99', 'fill'])
        self.assertEqual(conf['max_shade'], 4)

    def test_parse_args_all_args(self):
        conf = ghdecoy.parse_args(
            [
                './ghdecoy.py',
                '-f',
                '-k',
                '-n',
                '-s',
                '-d', '/fake/dir',
                '-l', 'python',
                '-m', '99',
                '-r', 'testrepo',
                '-p', '2',
                '-u', 'testuser',
                'append',
            ]
        )
        self.assertTrue(conf['dryrun'])
        self.assertTrue(conf['force_data'])
        self.assertTrue(conf['keep'])
        self.assertEqual(conf['wdir'], '/fake/dir')
        self.assertEqual(conf['lang'], 'python')
        self.assertEqual(conf['min_days'], 99)
        self.assertEqual(conf['repo'], 'testrepo')
        self.assertEqual(conf['max_shade'], 2)
        self.assertEqual(conf['user'], 'testuser')
        self.assertEqual(conf['action'], 'append')

    def test_parse_args_timeframe(self):
        conf = ghdecoy.parse_args(
            [
                './ghdecoy.py',
                '20130911',
            ]
        )
        self.assertEqual(conf['action'], 'timeframe')

    def test_parse_calendar(self):
        data = ['<svg width="721" height="110" class="js-calendar-graph-svg">',
                '<g transform="translate(20, 20)">',
                '<g transform="translate(0, 0)">',
                '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2015-01-01"/>',
                '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2015-01-02"/>',
                '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2015-01-03"/>',
                ]
        ret = ghdecoy.parse_calendar(data)
        self.assertDictEqual({'date': '2015-01-01T12:00:00',
                              'count': 4}, ret[0])
        self.assertDictEqual({'date': '2015-01-02T12:00:00',
                              'count': 4}, ret[1])
        self.assertDictEqual({'date': '2015-01-03T12:00:00',
                              'count': 1}, ret[2])

    def test_create_dataset_fill_center(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 0},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4, False, [], False)
        self.assertDictContainsSubset({'date': '2015-01-02T12:00:00'}, ret[0])
        self.assertDictContainsSubset({'date': '2015-01-03T12:00:00'}, ret[1])
        self.assertDictContainsSubset({'date': '2015-01-04T12:00:00'}, ret[2])

    def test_create_dataset_fill_start(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 0},
            {'date': '2015-01-02T12:00:00', 'count': 0},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4, False, [], False)
        self.assertDictContainsSubset({'date': '2015-01-01T12:00:00'}, ret[0])
        self.assertDictContainsSubset({'date': '2015-01-02T12:00:00'}, ret[1])
        self.assertDictContainsSubset({'date': '2015-01-03T12:00:00'}, ret[2])

    def test_create_dataset_fill_end(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4, False, [], False)
        self.assertDictContainsSubset({'date': '2015-01-03T12:00:00'}, ret[0])
        self.assertDictContainsSubset({'date': '2015-01-04T12:00:00'}, ret[1])
        self.assertDictContainsSubset({'date': '2015-01-05T12:00:00'}, ret[2])

    def test_create_dataset_fill_end_single_gap(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 1},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 1, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_fill_gap_to_small(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_fill_empty_input(self):
        data = []
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_fill_no_gap(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 1},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_append_center(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 0},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_append_start(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 0},
            {'date': '2015-01-02T12:00:00', 'count': 0},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_append_end(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4, False, [], False)
        self.assertDictContainsSubset({'date': '2015-01-03T12:00:00'}, ret[0])
        self.assertDictContainsSubset({'date': '2015-01-04T12:00:00'}, ret[1])
        self.assertDictContainsSubset({'date': '2015-01-05T12:00:00'}, ret[2])

    def test_create_dataset_append_end_single_gap(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 1},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 1, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_append_gap_to_small(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 1},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_append_empty_input(self):
        data = []
        ret = ghdecoy.create_dataset(data, 'append', 3, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_append_no_gap(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 1},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4, False, [], False)
        self.assertListEqual([], ret)

    def test_create_dataset_timeframe_single(self):
        data = [
            {'date': '2016-11-01T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'timeframe', 3, 4, False, {
            'singledates': [
                datetime.datetime(2016, 11, 1, 12, 0)
            ],
            'intervals': []
        }, False)
        self.assertDictContainsSubset({'date': '2016-11-01T12:00:00'}, ret[0])

    def test_create_dataset_timeframe_interval(self):
        data = [
            {'date': '2005-03-06T12:00:00', 'count': 0},
            {'date': '2005-03-07T12:00:00', 'count': 0},
            {'date': '2005-03-08T12:00:00', 'count': 0},
            {'date': '2005-03-09T12:00:00', 'count': 0},
            {'date': '2005-03-10T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'timeframe', 3, 4, False, {
            'singledates': [],
            'intervals': [[
                datetime.datetime(2005, 3, 7, 12, 0),
                datetime.datetime(2005, 3, 9, 12, 0)
            ]]
        }, False)
        self.assertDictContainsSubset({'date': '2005-03-09T12:00:00'}, ret[0])
        self.assertDictContainsSubset({'date': '2005-03-08T12:00:00'}, ret[1])
        self.assertDictContainsSubset({'date': '2005-03-07T12:00:00'}, ret[2])

    def test_create_dataset_timeframe_empty(self):
        data = [
            {'date': '2005-03-10T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'timeframe', 3, 4, False, {
            'singledates': [],
            'intervals': []
        }, False)
        self.assertListEqual([], ret)

    def test_create_template_https_wet(self):
        conf = {
            'ssh': False,
            'dryrun': False,
        }
        result = (
            '#!/bin/bash\n'
            'set -e\n'
            'REPO={0}\n'
            'git init $REPO\n'
            'cd $REPO\n'
            'touch decoy{1}\n'
            'git add decoy{1}\n'
            '{2}\n'
            'git remote add origin https://github.com/{3}/$REPO.git\n'
            'set +e\n'
            'git pull\n'
            'set -e\n'
            'git push -f -u origin master\n'
        )
        ret = ghdecoy.create_template(conf)
        self.assertEqual(result, ret)

    def test_create_template_ssh_dry(self):
        conf = {
            'ssh': True,
            'dryrun': True,
        }
        result = (
            '#!/bin/bash\n'
            'set -e\n'
            'REPO={0}\n'
            'git init $REPO\n'
            'cd $REPO\n'
            'touch decoy{1}\n'
            'git add decoy{1}\n'
            '{2}\n'
            'git remote add origin git@github.com:{3}/$REPO.git\n'
            'set +e\n'
            'git pull\n'
            'set -e\n'
        )
        ret = ghdecoy.create_template(conf)
        self.assertEqual(result, ret)

    def test_calendar_valid_true(self):
        cal = ['<svg width="721" height="110" class="js-calendar-graph-svg">',
               '<g transform="translate(20, 20)">',
               '<g transform="translate(0, 0)">',
               '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2014-05-20"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2014-05-21"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2014-05-22"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-05-23"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="3" data-date="2014-05-24"/>',
               '</g>',
               '<g transform="translate(13, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2014-05-25"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="2" data-date="2014-05-26"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="3" data-date="2014-05-27"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2014-05-28"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2014-05-29"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2014-05-30"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2014-05-31"/>',
               '</g>',
               '<g transform="translate(26, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2014-06-01"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-06-02"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2014-06-03"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2014-06-04"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2014-06-05"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-06-06"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2014-06-07"/>',
               '</g>',
               '<g transform="translate(39, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="3" data-date="2014-06-08"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-06-09"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2014-06-10"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2014-06-11"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2014-06-12"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-06-13"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2014-06-14"/>',
               '</g>',
               '<g transform="translate(52, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2014-06-15"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2014-06-16"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="3" data-date="2014-06-17"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2014-06-18"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2014-06-19"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2014-06-20"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2014-06-21"/>',
               '</g>',
               '<g transform="translate(65, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2014-06-22"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-06-23"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2014-06-24"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2014-06-25"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2014-06-26"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-06-27"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2014-06-28"/>',
               '</g>',
               '<g transform="translate(78, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="3" data-date="2014-06-29"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-06-30"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2014-07-01"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2014-07-02"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2014-07-03"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2014-07-04"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2014-07-05"/>',
               '</g>',
               '<g transform="translate(91, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2014-07-06"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="3" data-date="2014-07-07"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="3" data-date="2014-07-08"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2014-07-09"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2014-07-10"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-07-11"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2014-07-12"/>',
               '</g>',
               '<g transform="translate(104, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#44a340" data-count="4" data-date="2014-07-13"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#eeeeee" data-count="0" data-date="2014-07-14"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2014-07-15"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2014-07-16"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2014-07-17"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2014-07-18"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2014-07-19"/>',
               '</g>',
               '<g transform="translate(117, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2014-07-20"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#eeeeee" data-count="0" data-date="2014-07-21"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2014-07-22"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2014-07-23"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2014-07-24"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2014-07-25"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="3" data-date="2014-07-26"/>',
               '</g>',
               '<g transform="translate(130, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2014-07-27"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2014-07-28"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2014-07-29"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2014-07-30"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2014-07-31"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2014-08-01"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2014-08-02"/>',
               '</g>',
               '<g transform="translate(143, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#44a340" data-count="4" data-date="2014-08-03"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-08-04"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2014-08-05"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2014-08-06"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2014-08-07"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-08-08"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2014-08-09"/>',
               '</g>',
               '<g transform="translate(156, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#44a340" data-count="4" data-date="2014-08-10"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="2" data-date="2014-08-11"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2014-08-12"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2014-08-13"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2014-08-14"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#44a340" data-count="4" data-date="2014-08-15"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2014-08-16"/>',
               '</g>',
               '<g transform="translate(169, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="3" data-date="2014-08-17"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="2" data-date="2014-08-18"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2014-08-19"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2014-08-20"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2014-08-21"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-08-22"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2014-08-23"/>',
               '</g>',
               '<g transform="translate(182, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2014-08-24"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="3" data-date="2014-08-25"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2014-08-26"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2014-08-27"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2014-08-28"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2014-08-29"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="3" data-date="2014-08-30"/>',
               '</g>',
               '<g transform="translate(195, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="3" data-date="2014-08-31"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-09-01"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2014-09-02"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2014-09-03"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2014-09-04"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2014-09-05"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2014-09-06"/>',
               '</g>',
               '<g transform="translate(208, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="3" data-date="2014-09-07"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="3" data-date="2014-09-08"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2014-09-09"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2014-09-10"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2014-09-11"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-09-12"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2014-09-13"/>',
               '</g>',
               '<g transform="translate(221, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2014-09-14"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="3" data-date="2014-09-15"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2014-09-16"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2014-09-17"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2014-09-18"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-09-19"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2014-09-20"/>',
               '</g>',
               '<g transform="translate(234, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2014-09-21"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-09-22"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2014-09-23"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2014-09-24"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2014-09-25"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="3" data-date="2014-09-26"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2014-09-27"/>',
               '</g>',
               '<g transform="translate(247, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2014-09-28"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="2" data-date="2014-09-29"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2014-09-30"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2014-10-01"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2014-10-02"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2014-10-03"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2014-10-04"/>',
               '</g>',
               '<g transform="translate(260, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2014-10-05"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2014-10-06"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2014-10-07"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2014-10-08"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2014-10-09"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="3" data-date="2014-10-10"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2014-10-11"/>',
               '</g>',
               '<g transform="translate(273, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2014-10-12"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#eeeeee" data-count="0" data-date="2014-10-13"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="3" data-date="2014-10-14"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2014-10-15"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2014-10-16"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2014-10-17"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="3" data-date="2014-10-18"/>',
               '</g>',
               '<g transform="translate(286, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2014-10-19"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#eeeeee" data-count="0" data-date="2014-10-20"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2014-10-21"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2014-10-22"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2014-10-23"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="3" data-date="2014-10-24"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2014-10-25"/>',
               '</g>',
               '<g transform="translate(299, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2014-10-26"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="2" data-date="2014-10-27"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2014-10-28"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2014-10-29"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2014-10-30"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="3" data-date="2014-10-31"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2014-11-01"/>',
               '</g>',
               '<g transform="translate(312, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#44a340" data-count="4" data-date="2014-11-02"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2014-11-03"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2014-11-04"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2014-11-05"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2014-11-06"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2014-11-07"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2014-11-08"/>',
               '</g>',
               '<g transform="translate(325, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#44a340" data-count="4" data-date="2014-11-09"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2014-11-10"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#44a340" data-count="4" data-date="2014-11-11"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2014-11-12"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2014-11-13"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2014-11-14"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2014-11-15"/>',
               '</g>',
               '<g transform="translate(338, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="3" data-date="2014-11-16"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2014-11-17"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2014-11-18"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2014-11-19"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2014-11-20"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#44a340" data-count="4" data-date="2014-11-21"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2014-11-22"/>',
               '</g>',
               '<g transform="translate(351, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2014-11-23"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-11-24"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2014-11-25"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2014-11-26"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2014-11-27"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2014-11-28"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2014-11-29"/>',
               '</g>',
               '<g transform="translate(364, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2014-11-30"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2014-12-01"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2014-12-02"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2014-12-03"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2014-12-04"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2014-12-05"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2014-12-06"/>',
               '</g>',
               '<g transform="translate(377, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2014-12-07"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-12-08"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2014-12-09"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2014-12-10"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2014-12-11"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2014-12-12"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2014-12-13"/>',
               '</g>',
               '<g transform="translate(390, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#44a340" data-count="4" data-date="2014-12-14"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-12-15"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2014-12-16"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2014-12-17"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2014-12-18"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="3" data-date="2014-12-19"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2014-12-20"/>',
               '</g>',
               '<g transform="translate(403, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2014-12-21"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2014-12-22"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="3" data-date="2014-12-23"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2014-12-24"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2014-12-25"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="3" data-date="2014-12-26"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2014-12-27"/>',
               '</g>',
               '<g transform="translate(416, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2014-12-28"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2014-12-29"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2014-12-30"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2014-12-31"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2015-01-01"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2015-01-02"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="3" data-date="2015-01-03"/>',
               '</g>',
               '<g transform="translate(429, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2015-01-04"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2015-01-05"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2015-01-06"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="2" data-date="2015-01-07"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2015-01-08"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#44a340" data-count="4" data-date="2015-01-09"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2015-01-10"/>',
               '</g>',
               '<g transform="translate(442, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="3" data-date="2015-01-11"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2015-01-12"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2015-01-13"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2015-01-14"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2015-01-15"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2015-01-16"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2015-01-17"/>',
               '</g>',
               '<g transform="translate(455, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2015-01-18"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#eeeeee" data-count="0" data-date="2015-01-19"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2015-01-20"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-01-21"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2015-01-22"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2015-01-23"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2015-01-24"/>',
               '</g>',
               '<g transform="translate(468, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2015-01-25"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2015-01-26"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2015-01-27"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-01-28"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2015-01-29"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2015-01-30"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2015-01-31"/>',
               '</g>',
               '<g transform="translate(481, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2015-02-01"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="3" data-date="2015-02-02"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2015-02-03"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2015-02-04"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2015-02-05"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2015-02-06"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2015-02-07"/>',
               '</g>',
               '<g transform="translate(494, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#44a340" data-count="4" data-date="2015-02-08"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="3" data-date="2015-02-09"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2015-02-10"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-02-11"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2015-02-12"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2015-02-13"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2015-02-14"/>',
               '</g>',
               '<g transform="translate(507, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2015-02-15"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2015-02-16"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2015-02-17"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2015-02-18"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2015-02-19"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2015-02-20"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2015-02-21"/>',
               '</g>',
               '<g transform="translate(520, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="3" data-date="2015-02-22"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2015-02-23"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2015-02-24"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2015-02-25"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2015-02-26"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#44a340" data-count="4" data-date="2015-02-27"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2015-02-28"/>',
               '</g>',
               '<g transform="translate(533, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2015-03-01"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="2" data-date="2015-03-02"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="3" data-date="2015-03-03"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2015-03-04"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2015-03-05"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2015-03-06"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2015-03-07"/>',
               '</g>',
               '<g transform="translate(546, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2015-03-08"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2015-03-09"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="3" data-date="2015-03-10"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-03-11"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2015-03-12"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#44a340" data-count="4" data-date="2015-03-13"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2015-03-14"/>',
               '</g>',
               '<g transform="translate(559, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2015-03-15"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2015-03-16"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2015-03-17"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-03-18"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="2" data-date="2015-03-19"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2015-03-20"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2015-03-21"/>',
               '</g>',
               '<g transform="translate(572, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2015-03-22"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="2" data-date="2015-03-23"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2015-03-24"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2015-03-25"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#d6e685" data-count="1" data-date="2015-03-26"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2015-03-27"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#44a340" data-count="4" data-date="2015-03-28"/>',
               '</g>',
               '<g transform="translate(585, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2015-03-29"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="3" data-date="2015-03-30"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2015-03-31"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2015-04-01"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2015-04-02"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="3" data-date="2015-04-03"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2015-04-04"/>',
               '</g>',
               '<g transform="translate(598, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2015-04-05"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2015-04-06"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2015-04-07"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#8cc665" data-count="3" data-date="2015-04-08"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2015-04-09"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="3" data-date="2015-04-10"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="3" data-date="2015-04-11"/>',
               '</g>',
               '<g transform="translate(611, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#44a340" data-count="4" data-date="2015-04-12"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#44a340" data-count="4" data-date="2015-04-13"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#eeeeee" data-count="0" data-date="2015-04-14"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#44a340" data-count="4" data-date="2015-04-15"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#8cc665" data-count="3" data-date="2015-04-16"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2015-04-17"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="3" data-date="2015-04-18"/>',
               '</g>',
               '<g transform="translate(624, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2015-04-19"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#d6e685" data-count="1" data-date="2015-04-20"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2015-04-21"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-04-22"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2015-04-23"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2015-04-24"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#d6e685" data-count="1" data-date="2015-04-25"/>',
               '</g>',
               '<g transform="translate(637, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2015-04-26"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#1e6823" data-count="6" data-date="2015-04-27"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#d6e685" data-count="1" data-date="2015-04-28"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-04-29"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2015-04-30"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#d6e685" data-count="1" data-date="2015-05-01"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2015-05-02"/>',
               '</g>',
               '<g transform="translate(650, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#eeeeee" data-count="0" data-date="2015-05-03"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#eeeeee" data-count="0" data-date="2015-05-04"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2015-05-05"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-05-06"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#44a340" data-count="4" data-date="2015-05-07"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#8cc665" data-count="2" data-date="2015-05-08"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#8cc665" data-count="2" data-date="2015-05-09"/>',
               '</g>',
               '<g transform="translate(663, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#d6e685" data-count="1" data-date="2015-05-10"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#8cc665" data-count="2" data-date="2015-05-11"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="2" data-date="2015-05-12"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#d6e685" data-count="1" data-date="2015-05-13"/>',
               '<rect class="day" width="11" height="11" y="52" fill="#eeeeee" data-count="0" data-date="2015-05-14"/>',
               '<rect class="day" width="11" height="11" y="65" fill="#eeeeee" data-count="0" data-date="2015-05-15"/>',
               '<rect class="day" width="11" height="11" y="78" fill="#eeeeee" data-count="0" data-date="2015-05-16"/>',
               '</g>',
               '<g transform="translate(676, 0)">',
               '<rect class="day" width="11" height="11" y="0" fill="#8cc665" data-count="2" data-date="2015-05-17"/>',
               '<rect class="day" width="11" height="11" y="13" fill="#1e6823" data-count="5" data-date="2015-05-18"/>',
               '<rect class="day" width="11" height="11" y="26" fill="#8cc665" data-count="3" data-date="2015-05-19"/>',
               '<rect class="day" width="11" height="11" y="39" fill="#eeeeee" data-count="0" data-date="2015-05-20"/>',
               '</g>',
               '<text x="26" y="-5" class="month">Jun</text>',
               '<text x="91" y="-5" class="month">Jul</text>',
               '<text x="143" y="-5" class="month">Aug</text>',
               '<text x="208" y="-5" class="month">Sep</text>',
               '<text x="260" y="-5" class="month">Oct</text>',
               '<text x="312" y="-5" class="month">Nov</text>',
               '<text x="377" y="-5" class="month">Dec</text>',
               '<text x="429" y="-5" class="month">Jan</text>',
               '<text x="481" y="-5" class="month">Feb</text>',
               '<text x="533" y="-5" class="month">Mar</text>',
               '<text x="598" y="-5" class="month">Apr</text>',
               '<text x="650" y="-5" class="month">May</text>',
               '<text text-anchor="middle" class="wday" dx="-10" dy="9" style="display: none;">S</text>',
               '<text text-anchor="middle" class="wday" dx="-10" dy="22">M</text>',
               '<text text-anchor="middle" class="wday" dx="-10" dy="35" style="display: none;">T</text>',
               '<text text-anchor="middle" class="wday" dx="-10" dy="48">W</text>',
               '<text text-anchor="middle" class="wday" dx="-10" dy="61" style="display: none;">T</text>',
               '<text text-anchor="middle" class="wday" dx="-10" dy="74">F</text>',
               '<text text-anchor="middle" class="wday" dx="-10" dy="87" style="display: none;">S</text>',
               '</g>',
               '</svg>',
               ]
        self.assertTrue(ghdecoy.calendar_valid(cal))

    def test_calendar_valid_false(self):
        cal = ['<!DOCTYPE html>',
               '<html>',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               '0', '0', '0',
               '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
               ]
        self.assertFalse(ghdecoy.calendar_valid(cal))

    def test_calendar_valid_short_data(self):
        cal = ['<!DOCTYPE html>',
               '<html>',
               ]
        self.assertFalse(ghdecoy.calendar_valid(cal))

    def test_calendar_valid_empty_data(self):
        cal = []
        self.assertFalse(ghdecoy.calendar_valid(cal))

    def test_lang_valid_true(self):
        self.assertTrue(ghdecoy.lang_valid('python'))

    def test_lang_valid_false(self):
        self.assertFalse(ghdecoy.lang_valid('clojure'))

    def test_parse_timeframe_arg_invalid_arg(self):
        conf = {}
        self.assertFalse(ghdecoy.parse_timeframe_arg('foo', conf))

    def test_parse_timeframe_arg_one_single_date(self):
        conf = {}
        self.assertTrue(ghdecoy.parse_timeframe_arg('20160301', conf))
        self.assertDictEqual(conf, {'timeframe': {
            'singledates': [datetime.datetime(2016, 3, 1, 12, 0)],
            'intervals': []
        }})

    def test_parse_timeframe_arg_multiple_single_dates(self):
        conf = {}
        self.assertTrue(ghdecoy.parse_timeframe_arg(
            '20160301,20161224', conf))
        self.assertDictEqual(conf, {'timeframe': {
            'singledates': [
                datetime.datetime(2016, 3, 1, 12, 0),
                datetime.datetime(2016, 12, 24, 12, 0),
            ],
            'intervals': []
        }})

    def test_parse_timeframe_arg_one_interval(self):
        conf = {}
        self.assertTrue(ghdecoy.parse_timeframe_arg(
            '20160305-20160307', conf))
        self.assertDictEqual(conf, {'timeframe': {
            'singledates': [],
            'intervals': [[
                datetime.datetime(2016, 3, 5, 12, 0),
                datetime.datetime(2016, 3, 7, 12, 0)
            ]]
        }})

    def test_parse_timeframe_arg_multiple_intervals(self):
        conf = {}
        self.assertTrue(ghdecoy.parse_timeframe_arg(
            '20160202-20160205,20160321-20160322', conf))
        self.assertDictEqual(conf, {'timeframe': {
            'singledates': [],
            'intervals': [[
                datetime.datetime(2016, 2, 2, 12, 0),
                datetime.datetime(2016, 2, 5, 12, 0)
            ],[
                datetime.datetime(2016, 3, 21, 12, 0),
                datetime.datetime(2016, 3, 22, 12, 0)
            ]]
        }})

    def test_parse_timeframe_arg_one_single_date_one_interval(self):
        conf = {}
        self.assertTrue(ghdecoy.parse_timeframe_arg(
            '20160101,20160710-20160712', conf))
        self.assertDictEqual(conf, {'timeframe': {
            'singledates': [datetime.datetime(2016, 1, 1, 12, 0)],
            'intervals': [[
                datetime.datetime(2016, 7, 10, 12, 0),
                datetime.datetime(2016, 7, 12, 12, 0)
            ]]
        }})

    def test_parse_timeframe_arg_multiple_single_dates_and_intervals(self):
        conf = {}
        self.assertTrue(ghdecoy.parse_timeframe_arg(
            '20161101,19950307-19950309,20110303,19870912-19870913', conf))
        self.assertDictEqual(conf, {'timeframe': {
            'singledates': [
                datetime.datetime(2016, 11, 1, 12, 0),
                datetime.datetime(2011, 3, 3, 12, 0)
            ],
            'intervals': [[
                datetime.datetime(1995, 3, 7, 12, 0),
                datetime.datetime(1995, 3, 9, 12, 0)
            ],[
                datetime.datetime(1987, 9, 12, 12, 0),
                datetime.datetime(1987, 9, 13, 12, 0)
            ]]
        }})

    def test_parse_timeframe_arg_invalid_date_in_interval(self):
        conf = {}
        self.assertFalse(ghdecoy.parse_timeframe_arg(
            '20150301-20150332', conf))
        self.assertDictEqual(conf, {})

    def test_parse_timeframe_arg_across_month_boundaries(self):
        conf = {}
        self.assertTrue(ghdecoy.parse_timeframe_arg(
            '19990330-19990402', conf))
        self.assertDictEqual(conf, {'timeframe': {
            'singledates': [],
            'intervals': [[
                datetime.datetime(1999, 3, 30, 12, 0),
                datetime.datetime(1999, 4, 2, 12, 0)
            ]]
        }})

    def test_parse_timeframe_arg_across_year_boundaries(self):
        conf = {}
        self.assertTrue(ghdecoy.parse_timeframe_arg(
            '19991231-20000102', conf))
        self.assertDictEqual(conf, {'timeframe': {
            'singledates': [],
            'intervals': [[
                datetime.datetime(1999, 12, 31, 12, 0),
                datetime.datetime(2000, 1, 2, 12, 0)
            ]]
        }})

if __name__ == '__main__':
    unittest.main(buffer=True)
