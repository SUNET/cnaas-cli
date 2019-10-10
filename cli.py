import sys
import cmd
import getopt
import string
import readline
import requests

from model import Cli


class CnaasCli(cmd.Cmd):
    def __init__(self, host='localhost', port=5000, prompt='CNaaS# '):
        self.host = host
        self.port = port
        self.prompt = prompt
        self.intro = 'Welcome to CNaaS CLI, type help for help.'
        self.doc_header = 'CNaaS CLI.'
        self.url = 'http://{}:{}/api/v1.0'.format(self.host, self.port)
        self.cli = Cli('model/device.yml')
        self.commands = self.cli.commands()
        self.commands.append('no')
        self.commands.append('show')
        self.node_name = ''

    def complete(self, text, state):
        """ Get possible commands """
        line = readline.get_line_buffer().lstrip()
        if line.startswith('no '):
            line = line.split(' ')[-1]
        if len(line.split(' ')) < 2 and not line.endswith(' '):
            commands = self.commands
        else:
            commands = self.cli.get_attributes(self.node_name)
        completions = [x for x in commands if x.startswith(line.split(' ' )[-1])]
        try:
            if completions[state] in self.commands:
                self.node_name = completions[state]
            return completions[state]
        except IndexError:
            return None

    def helptext(self, line):
        return ''

    def parseline(self, line):
        line = line.strip()
        if not line:
            return None, None, line
        if line == '?':
            return None, None, self.helptext(line)
        i, n = 0, len(line)
        identchars = string.ascii_letters + string.digits + '_'
        while i < n and line[i] in identchars:
            i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def verify_command(self, cmd, args):
        err = []
        # Since the arguments come in pairs of keys and values we want
        # to get every second argument (key) here
        arglist = args.split()[::2]
        for arg in arglist:
            if arg not in self.cli.get_attributes(cmd):
                err.append('Invalid argument: {}'.format(arg))
        for arg in self.cli.get_mandatory(cmd):
            if arg not in arglist:
                err.append('Mandatory argument {} is missing'.format(arg))
        return err

    def cmd_post(self, cmd, args):
        url = self.url + '/' + self.cli.get_url(cmd)
        arglist = args.split()
        json = {'device': dict(zip(arglist[::2], arglist[1::2]))}
        res = requests.post(url=url, json=json)
        print(res.json)

    def do_command(self, command):
        cmd, args, line = self.parseline(command)
        if args is None:
            return line
        res = self.verify_command(cmd, args)
        if res != []:
            return res
        res = self.cmd_post(cmd, args)
        return res

    def cmdloop(self, completekey='tab'):
        """ Main loop """
        self.old_completer = readline.get_completer()
        readline.set_completer(self.complete)
        readline.parse_and_bind(completekey+": complete")
        line = input(self.prompt)
        print(self.do_command(line))
        readline.set_completer(self.old_completer)


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
        cli = CnaasCli(hostname, port)
        cli.cmdloop()
    except KeyboardInterrupt:
        print('\nSession closed, good bye!')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
