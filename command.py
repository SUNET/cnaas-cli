import os
import sys
import string
import readline

from model import Cli
from rest import Rest


class CliHandler():
    def __init__(self, host='localhost', port=5000, prompt='CNaaS# ',
                 model='cnaas.yml', token=None):
        if os.path.isfile('history.txt'):
            readline.read_history_file('history.txt')

        self.token = token
        self.prompt = prompt
        self.cli = Cli(model)
        self.builtin = ['no', 'show', 'help', 'history']
        self.node_name = ''
        self.commands = self.cli.commands()
        self.commands = self.commands + self.builtin

    def command_read_line(self):
        """Read a command from standard in.

        Returns the whole line and the last word.

        """
        line = readline.get_line_buffer().lstrip()

        if line.startswith('no') or line.startswith('show'):
            line = ' '.join(line.split(' ')[1:])

        return line, line.split(' ')[-1]

    def command_complete(self, text, state):
        """ Get possible commands based on what is already typed in.

        Returns a possible completion.

        """
        line, last = self.command_read_line()

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
        """ Return helptext for a certain command.

        Returns a helptext.
        """
        return 'Helptext here: ' + line

    def command_parseline(self, line):
        """ Parse a command line.

        Return the command together with its arguments.
        """

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
        """ Verify a command.

        Return and error string if the command is invalid.
        """

        err = []
        arglist = args.split()[::2]

        for arg in arglist:
            if arg not in self.cli.get_attributes(cmd):
                err.append('Invalid argument: {}'.format(arg))

        for arg in self.cli.get_mandatory(cmd):
            if arg not in arglist:
                err.append('Mandatory argument {} is missing'.format(arg))

        return err

    def command_post(self, cmd, args):
        """ Do REST POST call."

        Return error string if fails.
        """

        return 'Do POST here.'

    def command_builtin(self, command):
        """ Check if we have a builtin command.

        """
        if command == 'history':
            for i in range(readline.get_current_history_length()):
                print(readline.get_history_item(i + 1))
        if command == 'help' or command == '?':
            print("Help!")
        return ''

    def command_show(self, command):
        if command.split(' ')[0] == 'show':
            return True
        return False

    def command_no(self, command):
        if command.split(' ')[0] == 'no':
            return True
        return False

    def command_help(self, command):
        if command.split(' ')[0] == 'help':
            return True
        if '?' in command:
            return True
        return False

    def command_valid(self, command):
        if self.command_show(command) or self.command_no(command):
            command = command.split(' ')[1]
        else:
            command = command.split(' ')[0]
        if command not in self.commands:
            return False
        return True

    def command_strip(self, command):
        return ' '.join(command.split(' ')[1:])

    def command_execute(self, command):
        """ Execute commands.

        Return an error string if invalid.
        """
        if command in self.builtin:
            return self.command_builtin(command)
        if not self.command_valid(command):
            return 'Invalid command: ' + command
        if self.command_show(command):
            return Rest.get(self.command_strip(command), self.token)
        elif self.command_no(command):
            return Rest.delete(self.command_strip(command), self.token)
        elif self.command_help(command):
            return self.command_helptext(command)
        else:
            return Rest.post(command, self.token)
        return 'I have no idea what to do with this command'

    def command_loop(self, completekey='tab'):
        """ Main loop """
        self.old_completer = readline.get_completer()

        readline.set_completer(self.command_complete)
        readline.parse_and_bind(completekey+": complete")

        line = input(self.prompt)
        print(self.command_execute(line))

        readline.set_completer(self.old_completer)
        readline.write_history_file('history.txt')
