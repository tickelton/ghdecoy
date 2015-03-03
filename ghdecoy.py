#!/usr/bin/env python

import getopt, sys

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

    for o, a in opts:
        if o in ("-h", "--help"):
	    USAGE()
	    sys.exit()

    for a in args:
        print "{}".format(a)



if __name__ == '__main__':
    main()
