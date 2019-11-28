import string
import readline
import requests
import logging
from model import Cli

logging.basicConfig(filename='cli.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


class CliHandler():
    def __init__(self, host='localhost', port=5000, prompt='CNaaS# '):
        self.host = host
        self.port = port
        self.prompt = prompt
        self.intro = 'Welcome to CNaaS CLI, type help for help.'
        self.url = 'http://{}:{}/api/v1.0'.format(self.host, self.port)
        self.cli = Cli('model/device.yml')
        self.commands = self.cli.commands()
        self.builtin = ['no', 'show', 'help', 'history']
        self.commands = self.commands + self.builtin
        self.node_name = ''

    def command_read_line(self):
        """Read a command from standard in.

        Returns the whole line and the last word.

        """
        line = readline.get_line_buffer().lstrip()

        # We must handle the fact that we have special no and show
        # commands. We just strip the first word and treat it like any
        # other commands.
        if line.startswith('no') or line.startswith('show'):
            line = ' '.join(line.split(' ')[1:])
        last = line.split(' ')[-1]

        return line, last

    def command_complete(self, text, state):
        """ Get possible commands based on what is already typed in.

        Returns a possible completion.

        """
        line, last = self.command_read_line()

        # If we have less than two words, don't do argument
        # completion. Arguments are gathered from the YAML model.
        if len(line.split(' ')) < 2 and not line.endswith(' '):
            commands = self.commands
        else:
            commands = self.cli.get_attributes(self.node_name)

        completions = [x for x in commands if x.startswith(line.split(' ')[-1])]
        try:
            if completions[state] in self.commands:
                self.node_name = completions[state]
            return completions[state]
        except IndexError:
            return None

    def command_helptext(self, line):
        return ''

    def command_parseline(self, line):
        line = line.strip()
        if not line:
            return None, None, line
        if line == 'help':
            return None, None, self.command_helptext(line)
        i, n = 0, len(line)
        identchars = string.ascii_letters + string.digits + '_'
        while i < n and line[i] in identchars:
            i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def command_verify(self, cmd, args):
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

    def command_post(self, cmd, args):
        return 'Do POST here.'

    def command_builtin(self, command):
        if command == 'history':
            for i in range(readline.get_current_history_length()):
                print(readline.get_history_item(i + 1))
        return ''

    def command_execute(self, command):
        if command not in self.commands:
            return 'Invalid command'
        if command in self.builtin:
            return self.command_builtin(command)
        cmd, args, line = self.command_parseline(command)
        if args is None:
            return line
        res = self.command_verify(cmd, args)
        if res != []:
            return res
        res = self.command_post(cmd, args)
        return res

    def command_loop(self, completekey='tab'):
        """ Main loop """
        self.old_completer = readline.get_completer()
        readline.set_completer(self.command_complete)
        readline.parse_and_bind(completekey+": complete")
        line = input(self.prompt)
        print(self.command_execute(line))
        readline.set_completer(self.old_completer)
