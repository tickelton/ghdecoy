import unittest
import ghdecoy
import os


class GHDecoyOnlineTests(unittest.TestCase):
    """Unit tests for 'ghdecoy.py' that require an internet connection"""

    def test_get_calendar(self):
        cal = ghdecoy.get_calendar('tickelton')
        self.assertEqual(cal[0].find('<svg'), 0)


class GHDecoyIOTests(unittest.TestCase):
    """Unit tests for 'ghdecoy.py' that perform disk IO"""

    outfile = "/tmp/ghdecoy.sh"

    def test_create_script(self):
        conf = {
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
            'touch decoy\n'
            'git add decoy\n'
            '{1}\n'
            'git remote add origin git@github.com:{2}/$REPO.git\n'
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
            'echo 0 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-01T12:00:00 GIT_COMMITTER_DATE=2015-01-01T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 0 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-02T12:00:00 GIT_COMMITTER_DATE=2015-01-02T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 1 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-02T12:00:00 GIT_COMMITTER_DATE=2015-01-02T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 0 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-03T12:00:00 GIT_COMMITTER_DATE=2015-01-03T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 1 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-03T12:00:00 GIT_COMMITTER_DATE=2015-01-03T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 2 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-03T12:00:00 GIT_COMMITTER_DATE=2015-01-03T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 0 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-04T12:00:00 GIT_COMMITTER_DATE=2015-01-04T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 1 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-04T12:00:00 GIT_COMMITTER_DATE=2015-01-04T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 2 >> decoy\n',
            'GIT_AUTHOR_DATE=2015-01-04T12:00:00 GIT_COMMITTER_DATE=2015-01-04T12:00:00 git commit -a -m "ghdecoy" > /dev/null\n',
            'echo 3 >> decoy\n',
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

    def test_parse_args_invalid_shade(self):
        conf = ghdecoy.parse_args(['./ghdecoy.py', '-p', '99', 'fill'])
        self.assertEqual(conf['max_shade'], 4)

    def test_parse_args_all_args(self):
        conf = ghdecoy.parse_args(
            [
                './ghdecoy.py',
                '-k',
                '-n',
                '-s',
                '-d', '/fake/dir',
                '-m', '99',
                '-r', 'testrepo',
                '-p', '2',
                '-u', 'testuser',
                'append',
            ]
        )
        self.assertTrue(conf['dryrun'])
        self.assertTrue(conf['keep'])
        self.assertEqual(conf['wdir'], '/fake/dir')
        self.assertEqual(conf['min_days'], 99)
        self.assertEqual(conf['repo'], 'testrepo')
        self.assertEqual(conf['max_shade'], 2)
        self.assertEqual(conf['user'], 'testuser')
        self.assertEqual(conf['action'], 'append')

    def test_create_dataset_fill_center(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 0},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4)
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
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4)
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
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4)
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
        ret = ghdecoy.create_dataset(data, 'fill', 1, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_fill_gap_to_small(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_fill_empty_input(self):
        data = []
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_fill_no_gap(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 1},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'fill', 3, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_append_center(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 0},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_append_start(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 0},
            {'date': '2015-01-02T12:00:00', 'count': 0},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_append_end(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 0},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4)
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
        ret = ghdecoy.create_dataset(data, 'append', 1, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_append_gap_to_small(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 1},
            {'date': '2015-01-04T12:00:00', 'count': 0},
            {'date': '2015-01-05T12:00:00', 'count': 0},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_append_empty_input(self):
        data = []
        ret = ghdecoy.create_dataset(data, 'append', 3, 4)
        self.assertListEqual([], ret)

    def test_create_dataset_append_no_gap(self):
        data = [
            {'date': '2015-01-01T12:00:00', 'count': 1},
            {'date': '2015-01-02T12:00:00', 'count': 1},
            {'date': '2015-01-03T12:00:00', 'count': 1},
            {'date': '2015-01-04T12:00:00', 'count': 1},
            {'date': '2015-01-05T12:00:00', 'count': 1},
        ]
        ret = ghdecoy.create_dataset(data, 'append', 3, 4)
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
            'touch decoy\n'
            'git add decoy\n'
            '{1}\n'
            'git remote add origin https://github.com/{2}/$REPO.git\n'
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
            'touch decoy\n'
            'git add decoy\n'
            '{1}\n'
            'git remote add origin git@github.com:{2}/$REPO.git\n'
            'set +e\n'
            'git pull\n'
            'set -e\n'
        )
        ret = ghdecoy.create_template(conf)
        self.assertEqual(result, ret)


if __name__ == '__main__':
    unittest.main(buffer=True)
