#!/usr/bin/env python
"""Usage: ghdecoy.py [ARGS] CMD

  ARGS:
  -h|--help    : display this help message
  -k           : do not delete generated repository and upload script
  -n           : just create the decoy repo but don't push it to github
  -s           : push over ssh instead of https
  -v|--version : print version information and exit
  -d DIR       : directory to craft the the fake repository in (default: /tmp)
  -l LANG      : make decoy repo look like language LANG
  -m COUNT     : only fill gaps of at least COUNT days (default: 5)
  -r REPO      : use the repository REPO (default: decoy)
  -p NUM       : sets the darkest shade of contribution 'pixels' to be
                 created to NUM. Valid values are 1-4 (default: 4).
  -u USER      : use the username USER instead of the current unix user

  CMD          : one of the following:
                 fill   : fill all occurrences of 5 or more consecutive
                          days without commits with random noise
                 append : same as fill, but only fills the blank space
                          after the last existing commit
                 DATE[-DATE][,...] : fill only the given date(s). Overrides
                          '-m'. See man page for examples.
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
from datetime import datetime, timedelta

__version__ = '0.4.0'

content_templates = {
    'raw': {
        'ext': '',
        'data': 'echo {1} > decoy',
    },
    'c': {
        'ext': '.c',
        'data': 'echo \'#include <stdio.h>\' > decoy.c\n' + \
                'echo \'#include <stdlib.h>\' >> decoy.c\n' + \
                'echo \'\' >> decoy.c\n' + \
                'echo \'int main(void)\' >> decoy.c\n' + \
                'echo \'{{\' >> decoy.c\n' + \
                'echo \'  puts("Hello World{1}!");\' >> decoy.c\n' + \
                'echo \'  return EXIT_SUCCESS;\' >> decoy.c\n' + \
                'echo \'}}\' >> decoy.c\n',
    },
    'cpp': {
        'ext': '.cpp',
        'data': 'echo \'#include <iostream.h>\' > decoy.cpp\n' + \
                'echo \'\' >> decoy.cpp\n' + \
                'echo \'main()\' >> decoy.cpp\n' + \
                'echo \'{{\' >> decoy.cpp\n' + \
                'echo \'    cout << "Hello World{1}!" << endl;\' >> decoy.cpp\n' + \
                'echo \'    return 0;\' >> decoy.cpp\n' + \
                'echo \'}}\' >> decoy.cpp\n',
    },
    'csharp': {
        'ext': '.cs',
        'data': 'echo \'using System;\' > decoy.cs\n' + \
                'echo \'\' >> decoy.cs\n' + \
                'echo \'class Program\' >> decoy.cs\n' + \
                'echo \'{{\' >> decoy.cs\n' + \
                'echo \'    static void Main()\' >> decoy.cs\n' + \
                'echo \'    {{\' >> decoy.cs\n' + \
                'echo \'        Console.WriteLine("Hello, world{1}!");\' >> decoy.cs\n' + \
                'echo \'    }}\' >> decoy.cs\n' + \
                'echo \'}}\' >> decoy.cs\n',
    },
    'css': {
        'ext': '.css',
        'data': 'echo \'body:before {{\' > decoy.css\n' + \
                'echo \'    content: "Hello World{1}";\' >> decoy.css\n' + \
                'echo \'}}\' >> decoy.css\n',
    },
    'go': {
        'ext': '.go',
        'data': 'echo \'package main\' > decoy.go\n' + \
                'echo \'import "fmt"\' >> decoy.go\n' + \
                'echo \'func main() {{\' >> decoy.go\n' + \
                'echo \' fmt.Printf("Hello World{1}")\' >> decoy.go\n' + \
                'echo \'}}\' >> decoy.go\n',
    },
    'html': {
        'ext': '.html',
        'data': 'echo \'<HTML>\' > decoy.html\n' + \
                'echo \'<!-- Hello World in HTML -->\' >> decoy.html\n' + \
                'echo \'<HEAD>\' >> decoy.html\n' + \
                'echo \'<TITLE>Hello World{1}!</TITLE>\' >> decoy.html\n' + \
                'echo \'</HEAD>\' >> decoy.html\n' + \
                'echo \'<BODY>\' >> decoy.html\n' + \
                'echo \'Hello World!\' >> decoy.html\n' + \
                'echo \'</BODY>\' >> decoy.html\n' + \
                'echo \'</HTML>\' >> decoy.html\n',
    },
    'java': {
        'ext': '.java',
        'data': 'echo \'public class HelloWorld {{\' > decoy.java\n' + \
                'echo \'\' >> decoy.java\n' + \
                'echo \'    public static void main(String[] args) {{\' >> decoy.java\n' + \
                'echo \'        // Prints "Hello, World" to the terminal window.\' >> decoy.java\n' + \
                'echo \'        System.out.println("Hello, World{1}");\' >> decoy.java\n' + \
                'echo \'    }}\' >> decoy.java\n' + \
                'echo \'\' >> decoy.java\n' + \
                'echo \'}}\' >> decoy.java\n',
    },
    'jscript': {
        'ext': '.js',
        'data': 'echo \'function factorial{1}(n) {{\' > decoy.js\n' + \
                'echo \'    if (n == 0) {{\' >> decoy.js\n' + \
                'echo \'        return 1;\' >> decoy.js\n' + \
                'echo \'    }}\' >> decoy.js\n' + \
                'echo \'    return n * factorial(n - 1);\' >> decoy.js\n' + \
                'echo \'}}\' >> decoy.js\n',
    },
    'nasm': {
        'ext': '.asm',
        'data': 'echo \'        SECTION .data\' > decoy.asm\n' + \
                'echo \'\' >> decoy.asm\n' + \
                'echo \'        msg db "Hello, world{1}!",0xa ; \' >> decoy.asm\n' + \
                'echo \'        len equ $ - msg\' >> decoy.asm\n' + \
                'echo \'\' >> decoy.asm\n' + \
                'echo \'        SECTION .text\' >> decoy.asm\n' + \
                'echo \'        global main\' >> decoy.asm\n' + \
                'echo \'\' >> decoy.asm\n' + \
                'echo \'main:\' >> decoy.asm\n' + \
                'echo \'        mov     eax,4\' >> decoy.asm\n' + \
                'echo \'        mov     ebx,1\' >> decoy.asm\n' + \
                'echo \'        mov     ecx,msg\' >> decoy.asm\n' + \
                'echo \'        mov     edx,len\' >> decoy.asm\n' + \
                'echo \'        int     0x80\' >> decoy.asm\n' + \
                'echo \'\' >> decoy.asm\n' + \
                'echo \'        mov     eax,1\' >> decoy.asm\n' + \
                'echo \'        mov     ebx,0\' >> decoy.asm\n' + \
                'echo \'        int     0x80\' >> decoy.asm\n',
    },
    'perl': {
        'ext': '.pl',
        'data': 'echo \'#!/usr/bin/env perl\' > decoy.pl\n' + \
                'echo \'\' >> decoy.pl\n' + \
                'echo \'use warnings;\' >> decoy.pl\n' + \
                'echo \'use strict;\' >> decoy.pl\n' + \
                'echo \'\' >> decoy.pl\n' + \
                'echo \'print "Hello World{1}!";\' >> decoy.pl\n',
    },
    'php': {
        'ext': '.php',
        'data': 'echo \'<?php\' > decoy.php\n' + \
                'echo \'echo "Hello World{1}!";\' >> decoy.php\n' + \
                'echo \'?>  \' >> decoy.php\n',
    },
    'python': {
        'ext': '.py',
        'data': 'echo \'#!/usr/bin/env/python\' > decoy.py\n' + \
                'echo \'print "Hello World {1}"\' >> decoy.py',
    },
    'ruby': {
        'ext': '.rb',
        'data': 'echo \'class HelloWorld\' > decoy.rb\n' + \
                'echo \'   def initialize(name)\' >> decoy.rb\n' + \
                'echo \'      @name = name.capitalize\' >> decoy.rb\n' + \
                'echo \'   end\' >> decoy.rb\n' + \
                'echo \'   def speak\' >> decoy.rb\n' + \
                'echo \'      puts "Hello #{{@name}}{1}!"\' >> decoy.rb\n' + \
                'echo \'   end\' >> decoy.rb\n' + \
                'echo \'end\' >> decoy.rb\n' + \
                'echo \'\' >> decoy.rb\n' + \
                'echo \'hello = HelloWorld.new("World")\' >> decoy.rb\n' + \
                'echo \'hello.speak\' >> decoy.rb\n',
    }
}

known_languages = content_templates.keys()


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


def calendar_valid(cal):
    """Quick santiy check to see if the fetched calendar looks valid."""

    if len(cal) < 495:
        return False
    if cal[0].startswith('<svg '):
        return True
    return False


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


def lang_valid(lang):
    if lang in known_languages:
        return True
    return False

def parse_timeframe_arg(frame, conf):
    intervals = []
    singledates = []
    dates = frame.split(',')
    for d in dates:
        interval = d.split('-')
        if interval[0] != d:
            try:
                intervals.append(
                    [datetime.strptime(interval[0],"%Y%m%d") +
                        timedelta(hours=12),
                    datetime.strptime(interval[1],"%Y%m%d") +
                        timedelta(hours=12)])
            except ValueError:
                print "Invalid value: {}".format(d)
                return False
        else:
            try:
                singledates.append(datetime.strptime(d,"%Y%m%d") +
                                   timedelta(hours=12))
            except ValueError:
                print "Invalid value: {}".format(d)
                return False

    conf['timeframe'] = {
        'intervals': intervals,
        'singledates': singledates,
    }

    return True

def parse_args(argv):
    """Parses the script's arguments via getopt."""

    try:
        opts, args = getopt.getopt(
            argv[1:], "fhknsvd:l:m:p:r:u:", ["help", "version"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(1)

    conf = {
        'dryrun': False,
        'force_data': False,
        'keep': False,
        'lang': 'python',
        'max_shade': 4,
        'min_days': 5,
        'repo': 'decoy',
        'ssh': False,
        'timeframe': {},
        'user': os.getenv("USER"),
        'wdir': '/tmp'
    }

    for opt, arg in opts:
        if opt == "-d":
            conf['wdir'] = arg
        elif opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt == "-f":
            conf['force_data'] = True
        elif opt == "-k":
            conf['keep'] = True
        elif opt == "-l":
            conf['lang'] = arg
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

    if not lang_valid(conf['lang']):
        print "Invalid language: {}".format(conf['lang'])
        sys.exit(1)

    if args[0] in ("append", "fill"):
        conf['action'] = args[0]
    elif parse_timeframe_arg(args[0], conf) == True:
        conf['action'] = "timeframe"
    else:
        print "Invalid command: {}".format(args[0])
        sys.exit(1)

    if not conf['user']:
        print "Could not determine username; please use -u"
        sys.exit(1)

    return conf


def parse_calendar(cal):
    """Parse the raw svg data into a dictionary."""

    ret = []
    for line in cal:
        match = re.search(r'data-count="(\d+)".*data-date="(\d+-\d+-\d+)"',
                          line)
        if not match:
            continue
        ret.append({'date': match.group(2) + "T12:00:00",
                    'count': int(match.group(1))})
    return ret


def create_dataset(data_in, action, min_days, max_shade, force, timeframe):
    """Creates a data set representing the desired commits."""

    ret = []
    idx_start = -1
    idx_cur = 0
    idx_max = len(data_in) - 1
    if idx_max == -1:
        sys.stderr.write("Warning: Empty input; not creating dataset\n")
        return ret
    random.seed()

    if force:
        for i in range(0, idx_max):
            ret.append({'date': data_in[i]['date'],
                                'count': random.randint(0, max_shade)})
    elif action == 'timeframe':
        for in_date in timeframe['singledates']:
            in_iso = format(in_date.isoformat())
            for cal_date in data_in:
                if cal_date['date'] == in_iso:
                    ret.append({'date': cal_date['date'],
                        'count': random.randint(0, max_shade)})

        for in_interval in timeframe['intervals']:
            diff_days = (in_interval[1] - in_interval[0]).days
            while diff_days >= 0:
                in_iso = (in_interval[0] + timedelta(days=diff_days)).isoformat()

                for cal_date in data_in:
                    if cal_date['date'] == in_iso:
                        ret.append({'date': cal_date['date'],
                            'count': random.randint(0, max_shade)})

                diff_days -= 1
    else:
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


def get_content_template(lang):
    git_cmd = '\nGIT_AUTHOR_DATE={0} GIT_COMMITTER_DATE={0} git commit -a -m "ghdecoy" > /dev/null\n'

    return content_templates[lang]['data'] + git_cmd


def create_script(conf, data_out, template):
    """Creates a bash script that executes the actual git operations.

    The bash script created by this function creates a git repository, fills
    it with commits as specified via it's arguments and pushes it to github.
    """

    content_template = get_content_template(conf['lang'])
    fake_commits = []
    j = 0
    for entry in data_out:
        for i in range(entry['count']):
            fake_commits.append(
                content_template.format(entry['date'], j))
            j += 1
    script_name = ''.join([conf['wdir'], '/ghdecoy.sh'])
    script_fo = open(script_name, "w")
    script_fo.write(
        template.format(conf['repo'], content_templates[conf['lang']]['ext'], ''.join(fake_commits) ,conf['user']))
    script_fo.close()


def create_template(conf):
    """ Creates a template format string for the repo creation script."""
    template = (
        '#!/bin/bash\n'
        'set -e\n'
        'REPO={0}\n'
        'git init $REPO\n'
        'cd $REPO\n'
        'touch decoy{1}\n'
        'git add decoy{1}\n'
        '{2}\n'
    )

    if conf['ssh']:
        template = ''.join([template,
                            'git remote add origin git@github.com:{3}/$REPO.git\n'])
    else:
        template = ''.join([template,
                            'git remote add origin https://github.com/{3}/$REPO.git\n'])

    template = ''.join([template, 'set +e\ngit pull\nset -e\n'])

    if not conf['dryrun']:
        template = ''.join([template, 'git push -f -u origin master\n'])

    return template


def main():
    """The scripts main function."""

    conf = parse_args(sys.argv)
    ret = 0

    cal = get_calendar(conf['user'])
    if not cal:
        sys.stderr.write("Error: Unable to fetch calendar.\n")
        sys.exit(1)
    if not calendar_valid(cal):
        sys.stderr.write("Error: That doesn't look like contribution data.\n"
                         "Check user name and try again.\n")
        sys.exit(1)

    data_out = create_dataset(parse_calendar(cal), conf['action'],
                              conf['min_days'], conf['max_shade'],
                              conf['force_data'], conf['timeframe'])
    if not data_out:
        print "No commits to be pushed."
        sys.exit(ret)

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
