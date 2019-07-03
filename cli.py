import sys
import cmd
import yaml
import getopt
import string
import readline


class CnaasCli(cmd.Cmd):
    def __init__(self, host, port, prompt='CNaaS# '):
        self.host = host
        self.port = port
        self.prompt = prompt
        self.intro = 'Welcome to CNaaS CLI, type help for help.'
        self.doc_header = 'CNaaS CLI.'
        self.url = 'http://{}:{}/api/v1.0'.format(self.host, self.port)
        self.commands = []
        self.keywords = {'device': ['name', 'description', 'management_ip']}
        
    def command_add(self, name, args):
        """ Create a CLI command with help text based on the strcuture. """
        for item in args:
            if item == 'description':
                continue
            if item == 'url':
                continue
            if 'type' not in args[item]:
                raise Exception('Failed to parse command, type is missing')
            if 'mandatory' not in args[item]:
                raise Exception('Failed to parse command, mandatory missing')
            if 'description' not in args[item]:
                raise Exception('Failed to parse command, description missing')
        self.commands.append({'name': name, 'args': args})

    def complete(self, text, state):
        """ Get possible commands """
        origline = readline.get_line_buffer()
        line = origline.lstrip()
        if len(line.split(' ')) < 2 and not line.endswith(' '):
            completions = [x['name'] for x in self.commands if x['name'].startswith(line)]
        else:
            completions = []
            for item in self.commands:
                if item['name'] != line.split(' ')[0]:
                    continue
                for attr in item['args']:
                    if attr == 'url':
                        continue
                    completions.append(attr)
        try:
            return completions[state]
        except IndexError:
            return None

    def helptext(self, line):
        """ Print out the description for the suitable command """
        for item in self.commands:
            print(item['name'] + ': ' + item['args']['description'])
            print(' Arguments:')
            for arg in item['args']:
                if arg == 'description':
                    continue
                if arg == 'url':
                    continue
                descr = item['args'][arg]['description']
                mandatory = item['args'][arg]['mandatory']
                datatype = item['args'][arg]['type']
                print(' * {} (Mandatory? {}, Type: {}): {}'.format(arg,
                                                                   mandatory,
                                                                   datatype,
                                                                   descr))

    def parse_yaml(self, file):
        """ Parse YAML model and create CLI commands for each item. """
        with open(file, 'r') as fd:
            model = yaml.safe_load(fd)
        for item in model['model']:
            self.command_add(item, model['model'][item])

    def parseline(self, line):
        line = line.strip()
        if not line:
            return None, None, line
        if line == '?':
            print(self.helptext(line))
        i, n = 0, len(line)
        identchars = string.ascii_letters + string.digits + '_'
        while i < n and line[i] in identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def do_command(self, command):
        cmd, arg, line = self.parseline(command)

    def cmdloop(self, completekey='tab'):
        """ Main loop """
        self.old_completer = readline.get_completer()
        readline.set_completer(self.complete)
        readline.parse_and_bind(completekey+": complete")
        stop = None
        try:
            while not stop:
                try:
                    line = input(self.prompt)
                except EOFError:
                    line = 'EOF'
                if not len(line):
                    line = 'EOF'
                else:
                    line = line.rstrip('\r\n')
                stop = self.do_command(line)
        finally:
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
        cli.parse_yaml('model/device.yml')
        cli.cmdloop()
    except KeyboardInterrupt:
        print('\nSession closed, good bye!')
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
