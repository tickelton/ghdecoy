#!/usr/bin/env python

import getopt, sys, os
import urllib2
import re
import random
import math
import subprocess

def USAGE():
    print """Usage: ghdecoy.ph [-h|--help] [-d DIR] [-u USER] [-r REPO] COMMAND

  -h|--help : display this help message
  -d DIR    : directory to craft the the fake repository in
  -u USER   : use the username USER instead of the current unix user
  -r REPO   : use the repository REPO instead of the default 'decoy'

  COMMAND   : one of the following:
              fill   : fill all occurences of 3 or more days in a row
                       without commits with random noise
              append : same as fill, but only fills the blank space
                       after the last existing commit
"""

def get_calendar(user):
    """retrieves the github commit calendar data for a username"""
    url = 'https://github.com/users/' + user + '/contributions'
    try:
        page = urllib2.urlopen(url)
    except (urllib2.HTTPError,urllib2.URLError) as e:
        print ("There was a problem fetching data from {0}".format(url))
        print (e)
        raise SystemExit
    return page.readlines()

def get_factor(data):
    m = 0;
    for d in data:
        i = int(d['count'])
        if i > m:
            m = i

    f = m/4.0
    if f == 0: return 1
    f = math.ceil(f)
    f = int(f)
    return f


def cal_scale(data_out, data_in):
    scale_factor = get_factor(data_in)
    for d in data_out:
        d['count'] = d['count'] * scale_factor


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:r:u:", ["help"])
    except getopt.GetoptError as err:
        print str(err)
        USAGE()
        sys.exit(2)
    
    if len(args) != 1:
        USAGE()
        sys.exit(1)

    repo = 'decoy'
    user = os.getenv("USER")
    wdir = '/tmp'
    if args[0] in ("append", "fill"):
        action = args[0]
    else:
        print "Invalid command: {}".format(args[0])
        sys.exit(1)

    for o, a in opts:
        if o in ("-h", "--help"):
            USAGE()
            sys.exit()
        elif o == "-d":
            wdir = a
        elif o == "-r":
            repo = a
        elif o == "-u":
            user = a

    if not user:
        print "Could not determine username; please use -u"
        sys.exit(1)

    print "{} {} {}".format(user, repo, action)

    cal = get_calendar(user)

    data_in = []
    for line in cal:
        m = re.search('data-count="(\d+)".*data-date="(\d+-\d+-\d+)"', line)
        if m:
            data_in.append({'date': m.group(2) + "T12:00:00", 'count': m.group(1)})

    random.seed()

    data_out = []
    idx_start = -1
    idx_cur = 0
    for d in data_in:
        if idx_start > -1:
            if d['count'] != '0':
                for i in range(idx_start, idx_cur):
                    data_out.append({'date': data_in[i]['date'], 'count': random.randint(0,4)})
                idx_start = -1
        elif d['count'] == '0':
            idx_start = idx_cur
        idx_cur += 1

    if idx_start > -1:
        for i in range(idx_start, idx_cur):
            data_out.append({'date': data_in[i]['date'], 'count': random.randint(0,4)})

    cal_scale(data_out, data_in)

    outdir = '/media/ramdisk/'

    template = ('#!/bin/bash\n'
        'REPO={0}\n'
        'git init $REPO\n'
        'cd $REPO\n'
        'touch decoy\n'
        'git add decoy\n'
        '{1}\n'
        'git remote add origin git@github.com:{2}/$REPO.git\n'
        'git pull\n'
        'git push -f -u origin master\n')
    fake_commits = []
    for d in data_out:
        for i in range(d['count']):
            fake_commits.append('echo {1} >> decoy\nGIT_AUTHOR_DATE={0} GIT_COMMITTER_DATE={0} git commit -a -m "ghdecoy" > /dev/null\n'.format(d['date'], i))

    f = open('/media/ramdisk/ghdecoy.sh', "w")
    f.write(template.format(repo, "".join(fake_commits), user))
    f.close()

    os.chdir('/media/ramdisk')
    subprocess.call(['sh', '/media/ramdisk/ghdecoy.sh'])

if __name__ == '__main__':
    main()
