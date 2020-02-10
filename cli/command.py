import os
import sys
import string
import readline

from cli.terminal import print_hline
from cli.parser import CliParser
from cli.rest import Rest
from typing import Optional, List


class CliHandler():
    def __init__(self, url: Optional[str] = '',
                 prompt: Optional[str] = 'CNaaS# ',
                 model: Optional[str] = 'cnaas.yml',
                 token: Optional[str] = None,
                 banner: Optional[str] = '') -> None:
        """
        Constructur.

        Init CliParser and do some other stuff.

        Returns:

        """

        if os.path.isfile('history.txt'):
            readline.read_history_file('history.txt')

        self.url = url
        self.token = token
        self.prompt = prompt
        self.cli = CliParser(model)
        self.builtin = ['no', 'show', 'help', 'history', 'quit']
        self.modifiers = ['|', 'grep']
        self.node_name = ''
        self.commands = self.cli.get_commands()
        self.commands = self.commands + self.builtin

        if banner != '':
            print(banner)

    def read_line(self) -> tuple:
        """
        Read a command from standard in.

        Returns the whole line and the last word.

        """

        line = readline.get_line_buffer().lstrip()

        if line.startswith('no') or line.startswith('show'):
            line = ' '.join(line.split(' ')[1:])

        return line, line.split(' ')[-1]

    def complete(self, text: str, state: str) -> list:
        """
        Get possible commands based on what is already typed in.

        Returns a possible completion.

        """

        line, last = self.read_line()
        commandlen = len(line.split(' '))

        if commandlen < 2 and not line.endswith(' '):
            commands = self.commands
        else:
            commands = self.cli.get_attributes(self.node_name)
            commands += self.modifiers

        completions = [x for x in commands if x.startswith(line.split(' ')[-1])]

        try:
            if completions[state] in self.commands:
                self.node_name = completions[state]
            return completions[state]
        except IndexError:
            return None

    def __helptext_all_commands(self):
        """
        Print helptexts for all commands

        """

        print('Built-in commands:')
        print('  %-20s Disable the command that follows' % 'no')
        print('  %-20s Print this helptext' % 'help')
        print('  %-20s Print command history' % 'history')
        print('  %-20s Show the command that follows' % 'show')
        print('  %-20s Quit the CLI' % 'quit')
        print('')
        print('Other commands:', end='')
        print('')

        for command in self.cli.get_commands():
            description = self.cli.get_command_description(command)
            print('  %-20s %s' % (command, description))

        return '\n'

    def __helptext_command(self, line):
        """
        Print helptext for a single command
        """

        command = line.split(' ')[1]

        for attribute in self.cli.get_attributes(command):
            description = self.cli.get_attribute_description(command,
                                                             attribute)
            print('  %-20s %s' % (attribute, description))
        return ''

    def helptext(self, line: str) -> str:
        """
        Return helptext for a certain command.

        Returns a helptext.
        """

        if line.rstrip() == 'help':
            return self.__helptext_all_commands()

        return self.__helptext_command(line)

    def builtin_cmd(self, command: str) -> str:
        """
        Check if we have a builtin command.

        """

        command = command.split(' ')[0]
        if command == 'history':
            for i in range(readline.get_current_history_length()):
                print('  ' + readline.get_history_item(i + 1))
        elif command == 'help':
            for cmd in self.cli.get_commands():
                description = self.cli.get_command_description(cmd)
                print('%20s: %s' % (cmd, description))

        return ''

    def is_show(self, command: str) -> bool:
        """
        Find out whether we have a show command or not.
        """

        if command.split(' ')[0] == 'show':
            return True

        return False

    def is_no(self, command: str) -> bool:
        """
        Find out whether we have a no command or not.
        """

        if command.split(' ')[0] == 'no':
            return True

        return False

    def is_help(self, line: str) -> bool:
        """
        Find out whether we have a help command or not.
        """

        if 'help' in line:
            return True

        return False

    def validate(self, line: str) -> bool:
        """
        Find out if this is a valid command or not.
        """

        line = line.rstrip()

        if 'help' in line:
            return True

        if 'history' in line:
            return True

        if len(line.split(' ')) == 1:
            attributes = None
            command = line
        else:
            if line.split(' ')[0] in self.builtin:
                return True
            else:
                attributes = line.rstrip().split(' ')[1:]
                command = line.split(' ')[0]

        attributes_len = len(attributes)

        if attributes is not None and attributes_len % 2 != 0:
            print('Missing attribute values')
            return False

        if command not in self.commands:
            print('Command do not exist')
            return False

        spec_attributes = self.cli.get_attributes(command)
        if spec_attributes is None:
            return True
        if attributes is None and spec_attributes != []:
            print('Missing attributes')
            return False

        for attr in spec_attributes:
            if attr not in attributes and self.cli.get_mandatory(command,
                                                                 attr):
                print('Missing attribute: ' + attr)
                return False

        return True

    def strip(self, command: str) -> str:
        """
        Strip the command and return arguments.
        """

        return ' '.join(command.split(' ')[1:])

    def execute(self, line: str) -> str:
        """
        Execute commands.

        Return an error string if invalid.
        """

        modifier = ''

        if '|' in line:
            modifier = line.split('|')[-1]

        line = line.split('|')[0].lstrip().rstrip()
        command = line.split(' ')[0]

        # Empty command, silently ignore
        if line == '':
            return ''

        # Quit?
        if line == 'quit':
            print('Goodbye!')
            sys.exit(0)

        if line == 'history':
            return self.builtin_cmd('history')

        # Valid command?
        if not self.validate(line):
            return 'Invalid command: %s\n' % line

        if self.is_show(line):
            return Rest.get(self.strip(line), self.token, url=self.url,
                            modifier=modifier)
        elif self.is_no(line):
            return Rest.delete(self.strip(line), self.token, modifier=modifier)
        elif self.is_help(line):
            return self.helptext(line)
        else:
            if self.cli.get_methods(command) == ['get']:
                return Rest.get(line, self.token, url=self.url,
                                modifier=modifier)
            return Rest.post(line, self.token, url=self.url, modifier=modifier)
        return 'I have no idea what to do with this command'

    def loop(self) -> None:
        """
        Main loop

        """

        self.old_completer = readline.get_completer()

        readline.set_completer(self.complete)

        # Tab and ? will do completion
        readline.parse_and_bind('tab' + ': complete')
        readline.parse_and_bind('?' + ': complete')

        line = input(self.prompt)
        print(self.execute(line), end='')

        readline.set_completer(self.old_completer)
        readline.write_history_file('history.txt')
