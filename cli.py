import sys
import getopt

from cli.command import CliHandler


def usage():
    print('cli.py -u <url> -t <token>')
    sys.exit(0)


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
    try:
        cli = CliHandler(url, token=token, banner=banner)
        while True:
            cli.loop()
    except KeyboardInterrupt:
        print('\nSession closed, good bye!')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
