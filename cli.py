import sys
import getopt

from urllib.parse import urlparse
from cli.command import CliHandler
from signal import signal, SIGINT


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

    if uri.scheme == '' or uri.netloc == '':
        print('Could not parse URL.')
        sys.exit(0)

    return uri.netloc


def main(argv):
    url = ''
    token = ''
    banner = """
    _______   ,---.   .--.   ____       ____       .-'''-.
   /   __  \\  |    \\  |  | .'  __ `.  .'  __ `.   / _     \\
  | ,_/  \\__) |  ,  \\ |  |/   '  \\  \\/   '  \\  \\ (`' )/`--'
,-./  )       |  |\\_ \\|  ||___|  /  ||___|  /  |(_ o _).
\\  '_ '`)     |  _( )_\\  |   _.-`   |   _.-`   | (_,_). '.
 > (_)  )  __ | (_ o _)  |.'   _    |.'   _    |.---.  \\  :
(  .  .-'_/  )|  (_,_)\\  ||  _( )_  ||  _( )_  |\\    `-'  |
 `-'`-'     / |  |    |  |\\ (_ o _) /\\ (_ o _) / \\       /
   `._____.'  '--'    '--' '.(_,_).'  '.(_,_).'   `-...-'


CNaaS - Command Line Interface\n
(C) SUNET (http://www.sunet.se), 2020


'Type "help" for help.


"""

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
        usage()

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
