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
        elif line.startswith('help '):
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

    def __helptext_all_commands(self):
        for command in self.cli.get_commands():
            description = self.cli.get_command_description(command)
            print('  %-20s %s' % (command, description))
        return ''

    def __helptext_command(self, line):
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
                print(readline.get_history_item(i + 1))
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

    def is_help(self, command: str) -> bool:
        """
        Find out whether we have a help command or not.
        """

        if 'help' in command:
            return True
        return False

    def validate(self, line: str) -> bool:
        """
        Find out if this is a valid command or not.
        """

        line = line.rstrip()

        if 'help' in line:
            return True

        if len(line.split(' ')) == 1:
            attributes = None
            command = line
        else:
            if line.split(' ')[0] in self.builtin:
                return True
            else:
                attributes = line.split(' ')[1:]
                command = line.split(' ')[0]

        if attributes is not None and len(attributes) % 2 != 0:
            print('Missing attribute values')
            return False

        if command not in self.commands:
            print('Command do not exist')
            return False

        spec_attributes = self.cli.get_attributes(command)
        if spec_attributes is None:
            return True
        if attributes is None and spec_attributes is not None:
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

    def new_line(self, msg: Optional[str] = ''):
        print(msg)

    def execute(self, command: str) -> str:
        """
        Execute commands.

        Return an error string if invalid.
        """

        # Empty command, silently ignore
        if command == '':
            return ''

        # Quit?
        if command == 'quit':
            print('Goodbye!')
            sys.exit(0)

        # Valid command?
        if not self.validate(command):
            return 'Invalid command: %s\n' % command

        if self.is_show(command):
            return Rest.get(self.strip(command), self.token, url=self.url)
        elif self.is_no(command):
            return Rest.delete(self.strip(command), self.token)
        elif self.is_help(command):
            return self.helptext(command)
        else:
            return Rest.post(command, self.token, url=self.url)
        return 'I have no idea what to do with this command'

    def loop(self, completekey: Optional[str] = 'tab') -> None:
        """
        Main loop
        """
        self.old_completer = readline.get_completer()

        readline.set_completer(self.complete)
        readline.parse_and_bind(completekey+": complete")

        line = input(self.prompt)
        print(self.execute(line), end='')

        readline.set_completer(self.old_completer)
        readline.write_history_file('history.txt')
