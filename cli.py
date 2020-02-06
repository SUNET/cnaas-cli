import sys
import getopt

from urllib.parse import urlparse
from cli.command import CliHandler
from cli.parser import CliParser
from signal import signal, SIGINT


def handler_sigint(signal_received, frame):
    pass


def usage():
    print('cli.py -u <url> -t <token>')
    sys.exit(0)


def get_domain(url):
    uri = urlparse(url)
    return uri.netloc


def main(argv):
    url = ''
    token = ''
    banner = """\n\n
    _______   ,---.   .--.   ____       ____       .-'''-.
   /   __  \\  |    \\  |  | .'  __ `.  .'  __ `.   / _     \\
  | ,_/  \\__) |  ,  \\ |  |/   '  \\  \\/   '  \\  \\ (`' )/`--'
,-./  )       |  |\\_ \\|  ||___|  /  ||___|  /  |(_ o _).
\\  '_ '`)     |  _( )_\\  |   _.-`   |   _.-`   | (_,_). '.
 > (_)  )  __ | (_ o _)  |.'   _    |.'   _    |.---.  \\  :
(  .  .-'_/  )|  (_,_)\\  ||  _( )_  ||  _( )_  |\\    `-'  |
 `-'`-'     / |  |    |  |\\ (_ o _) /\\ (_ o _) / \\       /
   `._____.'  '--'    '--' '.(_,_).'  '.(_,_).'   `-...-'

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
        cli.new_line(str(str(e)))
    except EOFError:
        print('\nGoodbye!')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
