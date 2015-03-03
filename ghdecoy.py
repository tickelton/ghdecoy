#!/usr/bin/env python

import getopt, sys, os
import urllib2

def USAGE():
    print """Usage: ghdecoy.ph [-h|--help] [-u USER] [-r REPO] COMMAND

  -h|--help : display this help message
  -u USER   : use the username USER instead of the current unix user
  -r REPO   : use the repository REPO instead of the default 'decoy'

  COMMAND   : one of the following:
              init : initialize the calendar with random noise
              fill : fill all occurences of 3 or more days in a row
                     without commits with random noise
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

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hr:u:", ["help"])
    except getopt.GetoptError as err:
        print str(err)
        USAGE()
        sys.exit(2)
    
    if len(args) != 1:
        USAGE()
        sys.exit(1)

    repo = 'decoy'
    user = os.getenv("USER")
    if args[0] in ("init", "fill"):
        action = args[0]
    else:
        print "Invalid command: {}".format(args[0])
        sys.exit(1)

    for o, a in opts:
        if o in ("-h", "--help"):
            USAGE()
            sys.exit()
        elif o == "-r":
            repo = a
        elif o == "-u":
            user = a

    if not user:
        print "Could not determine username; please use -u"
        sys.exit(1)

    print "{} {} {}".format(user, repo, action)

    cal = get_calendar(user)


if __name__ == '__main__':
    main()
