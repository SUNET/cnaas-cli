import sys
import cmd
import getopt
import string
import logging

from command import CliHandler


def usage():
    print('cli.py -h <hostname> -p <port')
    sys.exit(0)


def main(argv):
    hostname = ''
    port = 5000

    try:
        opts, args = getopt.getopt(argv, 'h:p:')
    except getopt.GetoptError:
        usage(argv)
    for opt, arg in opts:
        if opt == '-h':
            hostname = arg
        if opt == '-p':
            port = arg
    if hostname == '':
        usage()
    try:
        cli = CliHandler(hostname, port)
        while True:
            cli.command_loop()
    except KeyboardInterrupt:
        print('\nSession closed, good bye!')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
