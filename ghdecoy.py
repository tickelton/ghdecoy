#!/usr/bin/env python
"""Usage: ghdecoy.py [ARGS] CMD

  ARGS:
  -h|--help    : display this help message
  -k           : do not delete generated repository and upload script
  -n           : just create the decoy repo but don't push it to github
  -s           : push over ssh instead of https
  -v|--version : print version information and exit
  -d DIR       : directory to craft the the fake repository in
  -m COUNT     : only fill gaps of at least COUNT days (default=5)
  -r REPO      : use the repository REPO instead of the default 'decoy'
  -p NUM       : sets the darkest shade of contribution 'pixels' to be
                 created to NUM. Valid values are 1-4 (default=4).
  -u USER      : use the username USER instead of the current unix user

  CMD          : one of the following:
                 fill   : fill all occurrences of 5 or more consecutive
                          days without commits with random noise
                 append : same as fill, but only fills the blank space
                          after the last existing commit
"""

import getopt
import sys
import os
import urllib2
import re
import random
import math
import subprocess
import shutil

__version__ = '0.1.0'


def usage():
    """Prints the usage message."""

    print __doc__


def version():
    """Prints version information."""

    print "ghdecoy.py {}".format(__version__)


def get_calendar(user):
    """Retrieves the given user's contribution data from Github."""

    url = 'https://github.com/users/' + user + '/contributions'
    try:
        page = urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError) as err:
        print "There was a problem fetching data from {0}".format(url)
        print err
        return None
    return page.readlines()


def get_factor(data):
    """Calculates the factor by which the calender data has to be scaled."""

    max_val = 0
    for entry in data:
        if entry['count'] < 0:
            sys.stderr.write(
                "Warning: Found invalid value ({}) at {}.\n".format(
                    entry['count'], entry['date']
                )
            )
            entry['count'] = 0
        if entry['count'] > max_val:
            max_val = entry['count']

    factor = max_val / 4.0
    if factor == 0:
        return 1
    factor = math.floor(factor)
    factor = int(factor)
    return factor


def cal_scale(scale_factor, data_out):
    """Scales the calendar data by a given factor."""

    for entry in data_out:
        entry['count'] *= scale_factor


def parse_args(argv):
    """Parses the script's arguments via getopt."""

    try:
        opts, args = getopt.getopt(
            argv[1:], "hknsvd:m:r:p:u:", ["help", "version"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(1)

    conf = {
        'dryrun': False,
        'keep': False,
        'max_shade': 4,
        'min_days': 5,
        'repo': 'decoy',
        'ssh': False,
        'user': os.getenv("USER"),
        'wdir': '/tmp'
    }

    for opt, arg in opts:
        if opt == "-d":
            conf['wdir'] = arg
        elif opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt == "-k":
            conf['keep'] = True
        elif opt == "-m":
            conf['min_days'] = int(arg)
        elif opt == "-n":
            conf['dryrun'] = True
        elif opt == "-p":
            val = int(arg)
            if 0 < val < 5:
                conf['max_shade'] = val
        elif opt == "-r":
            conf['repo'] = arg
        elif opt == "-s":
            conf['ssh'] = True
        elif opt == "-u":
            conf['user'] = arg
        elif opt in ("-v", "--version"):
            version()
            sys.exit(0)

    if len(args) != 1:
        usage()
        sys.exit(1)

    if args[0] in ("append", "fill"):
        conf['action'] = args[0]
    else:
        print "Invalid command: {}".format(args[0])
        sys.exit(1)

    if not conf['user']:
        print "Could not determine username; please use -u"
        sys.exit(1)

    return conf


def create_dataset(data_in, action, min_days, max_shade):
    """Creates a data set representing the desired commits."""

    ret = []
    idx_start = -1
    idx_cur = 0
    idx_max = len(data_in) - 1
    if idx_max == -1:
        sys.stderr.write("Warning: Empty input; not creating dataset\n")
        return ret
    random.seed()

    if action == 'append':
        idx_cur = idx_max
        for entry in reversed(data_in):
            if entry['count']:
                break
            idx_cur -= 1

    # NOTE: This won't fill the last day if it is not preceded by at least one
    # other empty day. Doesn't matter though, as we're only filling blocks of
    # at least three continuous empty days.
    for entry in data_in[idx_cur:]:
        if entry['count'] or idx_cur == idx_max:
            if idx_start > -1:
                idx_range = range(idx_start,
                                  idx_cur if entry['count'] else idx_cur + 1)
                idx_start = -1
                if len(idx_range) < min_days:
                    idx_cur += 1
                    continue
                for i in idx_range:
                    ret.append({'date': data_in[i]['date'],
                                'count': random.randint(0, max_shade)})
        elif idx_start == -1:
            idx_start = idx_cur
        idx_cur += 1

    cal_scale(get_factor(data_in), ret)
    return ret


def create_script(conf, data_out, template):
    """Creates a bash script that executes the actual git operations.

    The bash script created by this function creates a git repository, fills
    it with commits as specified via it's arguments and pushes it to github.
    """

    fake_commits = []
    for entry in data_out:
        for i in range(entry['count']):
            fake_commits.append(
                'echo {1} >> decoy\nGIT_AUTHOR_DATE={0} GIT_COMMITTER_DATE={0} git commit -a -m "ghdecoy" > /dev/null\n'.format(
                    entry['date'], i))
    script_name = ''.join([conf['wdir'], '/ghdecoy.sh'])
    script_fo = open(script_name, "w")
    script_fo.write(
        template.format(conf['repo'], ''.join(fake_commits), conf['user']))
    script_fo.close()


def create_template(conf):
    """ Creates a template format string for the repo creation script."""
    template = (
        '#!/bin/bash\n'
        'set -e\n'
        'REPO={0}\n'
        'git init $REPO\n'
        'cd $REPO\n'
        'touch decoy\n'
        'git add decoy\n'
        '{1}\n'
    )

    if conf['ssh']:
        template = ''.join([template,
            'git remote add origin git@github.com:{2}/$REPO.git\n'])
    else:
        template = ''.join([template,
            'git remote add origin https://github.com/{2}/$REPO.git\n'])

    template = ''.join([template, 'set +e\ngit pull\nset -e\n'])

    if not conf['dryrun']:
        template = ''.join([template, 'git push -f -u origin master\n'])

    return template


def main():
    """The scripts main function."""

    conf = parse_args(sys.argv)
    ret = 0

    print "{} {} {}".format(conf['user'], conf['repo'], conf['action'])

    cal = get_calendar(conf['user'])
    if not cal:
        sys.exit(1)

    data_in = []
    for line in cal:
        match = re.search(r'data-count="(\d+)".*data-date="(\d+-\d+-\d+)"',
                          line)
        if not match:
            continue
        data_in.append({'date': match.group(2) + "T12:00:00",
                        'count': int(match.group(1))})

    data_out = create_dataset(data_in, conf['action'],
                              conf['min_days'], conf['max_shade'])

    create_script(conf, data_out, create_template(conf))

    os.chdir(conf['wdir'])
    try:
        subprocess.check_call(['sh', './ghdecoy.sh'])
    except subprocess.CalledProcessError as err:
        print err
        ret = 1

    if not conf['keep']:
        shutil.rmtree(conf['repo'], True)
        os.remove('ghdecoy.sh')

    sys.exit(ret)


if __name__ == '__main__':
    main()
