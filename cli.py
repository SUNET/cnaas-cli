import sys
import getopt

from urllib.parse import urlparse
from cli.command import CliHandler
from cli.parser import CliParser
from signal import signal, SIGINT


def handler_sigint(signal_received, frame):
    """
    Handle Ctrl+C

    """

    pass


def usage():
    """
    Print usage string

    """
    print('cli.py -u <url> -t <token>')
    sys.exit(0)


def get_domain(url):
    """
    Get domain name from URL

    """

    uri = urlparse(url)

    return uri.netloc


def main(argv):
    url = ''
    token = ''
    banner = """
CNaaS - Command Line Interface\n
(C) SUNET (http://www.sunet.se), 2020
"""

    signal(SIGINT, handler_sigint)

    try:
        opts, args = getopt.getopt(argv, 'u:t:')
    except getopt.GetoptError:
        usage(argv)
    for opt, arg in opts:
        if opt == '-u':
            url = arg
        if opt == '-t':
            token = arg
    if token == '':
        usage()

    if url == '':
        try:
            cli = CliParser('cnaas.yml')
            url = cli.get_base_url()
        except Exception:
            print('Could not find an URL.')
            sys.exit(0)

    domain = get_domain(url)
    prompt = 'CNaaS NMS (%s)# ' % domain

    try:
        cli = CliHandler(url, token=token, banner=banner, prompt=prompt)
        while True:
            cli.loop()
    except KeyboardInterrupt as e:
        print('\n' + (str(str(e))))
    except EOFError:
        print('\nGoodbye!')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
