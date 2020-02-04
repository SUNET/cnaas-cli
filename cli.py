import sys
import getopt

from cli.command import CliHandler


def usage():
    print('cli.py -h <hostname> -p <port> -t <token>')
    sys.exit(0)


def main(argv):
    hostname = ''
    port = 5000
    token = ''

    try:
        opts, args = getopt.getopt(argv, 'h:p:t:')
    except getopt.GetoptError:
        usage(argv)
    for opt, arg in opts:
        if opt == '-h':
            hostname = arg
        if opt == '-p':
            port = arg
        if opt == '-t':
            token = arg
    if hostname == '' or token == '':
        usage()
    try:
        cli = CliHandler(hostname, port, token=token)
        while True:
            cli.loop()
    except KeyboardInterrupt:
        print('\nSession closed, good bye!')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
