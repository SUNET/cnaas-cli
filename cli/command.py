import os
import re
import sys
import time
import signal
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
        self.builtin = ['no', 'show', 'help', 'history', 'quit', 'update']
        self.modifiers = ['|']
        self.modifiers_commands = ['grep', 'monitor']

        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('?: complete')
        readline.parse_and_bind('"\\C-l": clear-screen')
        readline.set_completion_display_matches_hook(self.print_suggestions)

        if banner != '':
            print(banner)

    def read_line(self) -> tuple:
        """
        Read a command from standard in.

        Returns the whole line and the last word.

        """

        full_line = readline.get_line_buffer().lstrip()
        line = full_line

        if any(line.startswith(x) for x in ['no', 'show', 'update']):
            command = line.split(' ')[1]
            line = ' '.join(line.split(' ')[1:])
        else:
            command = line.split(' ')[0]

        return line, full_line, command

    def complete(self, text: str, state: str) -> list:
        """
        Get possible commands based on what is already typed in.

        Returns a possible completion.

        """
        line, full_line, command = self.read_line()
        commandlen = len(line.split(' '))

        if re.match(r'.+\|.*', line):
            commands = self.modifiers_commands
        elif commandlen < 2 and not line.endswith(' '):
            if re.findall(r'\s*no.*', full_line):
                commands = self.cli.get_delete() + self.modifiers
            elif re.match(r'\s*update.*', full_line):
                commands = self.cli.get_update() + self.modifiers
            elif re.match(r'\s*show.*', full_line):
                commands = self.cli.get_show() + self.modifiers
            else:
                commands = self.cli.get_not_show()
                commands += self.modifiers + self.builtin
        else:
            if re.findall(r'\s*show.*', full_line):
                commands = self.cli.get_attributes_show(command)
                commands += self.modifiers
            elif re.findall(r'\s*no.*', full_line):
                commands = self.cli.get_attributes_no(command) + self.modifiers
            else:
                commands = self.cli.get_attributes(command)
                commands += self.modifiers

        split_line = line.split(' ')[-1]
        completions = [x for x in commands if x.startswith(split_line)]

        try:
            return completions[state]
        except IndexError:
            return None

    def helptext_all_commands(self):
        """
        Print helptexts for all commands

        """

        print('Built-in commands:')
        print('  %-20s Disable the command that follows' % 'no')
        print('  %-20s Print this helptext' % 'help')
        print('  %-20s Print command history' % 'history')
        print('  %-20s Show the command that follows' % 'show')
        print('  %-20s Quit the CLI' % 'quit')
        print('\nModifiers')
        print('  %-20s Grep after a given string' % 'grep')
        print('  %-20s Monitor the output of a show command' % 'monitor')
        print('\nOther commands:')

        for command in self.cli.get_commands():
            description = self.cli.get_command_description(command)
            print('  %-20s %s' % (command, description))

        return '\n'

    def helptext_command(self, line):
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
            return self.helptext_all_commands()

        return self.helptext_command(line)

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

    def is_update(self, command: str) -> bool:
        """
        Find out whether we have an update command or not.
        """

        if command.split(' ')[0] == 'update':
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

        res = True
        line = line.rstrip()

        if self.is_help(line):
            return True

        if self.is_show(line):
            return True

        if len(line.split(' ')) == 1:
            attributes = None
            command = line
        else:
            command = line.split(' ')[0]

            if any(line.startswith(x) for x in ['no', 'show', 'update']):
                attributes = line.rstrip().split(' ')[2:]
                command = line.split(' ')[1]
            else:
                attributes = line.rstrip().split(' ')[1:]
                command = line.split(' ')[0]

        if command not in self.cli.get_commands():
            print('Command does not exist')
            return False

        spec_attributes = self.cli.get_attributes(command)

        if spec_attributes is None and attributes is None:
            return True

        if spec_attributes is None and attributes is not None:
            print('Command did not expect any attributes')
            return False

        for attr in spec_attributes:
            if attributes is not None:
                if attr in attributes:
                    continue
            if self.cli.get_mandatory(command, attr):
                print('Missing mandatory attribute: ' + attr)
                res = False

        return res

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
        if line == 'quit' or line == 'exit':
            print('Goodbye!')
            sys.exit(0)

        if line == 'history':
            return self.builtin_cmd('history')

        # Valid command?
        if not self.validate(line):
            return 'Invalid command: %s\n\n' % line

        if self.is_show(line):
            return Rest.get(self.strip(line), self.token, self.url,
                            modifier=modifier)
        elif self.is_no(line):
            return Rest.delete(self.strip(line), self.token, self.url,
                               modifier=modifier)
        elif self.is_update(line):
            return Rest.put(self.strip(line), self.token, self.url,
                            modifier=modifier)
        elif self.is_help(line):
            return self.helptext(line)
        else:
            if self.cli.get_use_put(command):
                return Rest.put(line, self.token, self.url,
                                modifier=modifier)
            else:
                return Rest.post(line, self.token, url=self.url,
                                 modifier=modifier)

        return 'I have no idea what to do with this command.\n'

    def print_suggestions(self, substitution: str, matches: list,
                          longest_match_length: int) -> None:
        """
        Print helptexts for commands and arguments.

        """

        line = readline.get_line_buffer()
        cmdlist = line.split(' ')

        print('')
        if len(cmdlist) == 1 or len(cmdlist) == 2 and cmdlist[0] in self.builtin:
            for match in matches:
                if match == 'help':
                    description = 'Print helptexts'
                elif match == 'history':
                    description = 'Print command history'
                elif match == 'no':
                    description = 'Disable the command that follows'
                elif match == 'show':
                    description = 'Display details'
                elif match == 'update':
                    description = 'Update the command that follows'
                elif match == 'exit' or match == 'quit':
                    description = 'Exit the CLI'
                elif match == '|':
                    description = 'Modify the output'
                else:
                    description = self.cli.get_command_description(match)
                print('  %-20s %s' % (match, description))
        else:
            if cmdlist[0] in self.builtin:
                command = cmdlist[1]
            else:
                command = cmdlist[0]
            if self.cli.get_attributes(command) != []:
                for match in matches:
                    description = self.cli.get_attribute_description(command,
                                                                     match)
                    mandatory = self.cli.get_mandatory(command, match)

                    if mandatory:
                        print('  %-20s %s (MANDATORY)' % (match, description))
                    else:
                        print('  %-20s %s' % (match, description))
        print('')
        print(self.prompt, line, sep='', end='', flush=True)

    def loop(self) -> None:
        """
        Main loop

        """

        self.old_completer = readline.get_completer()

        line = input(self.prompt)
        job_status = r'.*Status:.*(FINISHED|ABORTED|EXCEPTION)'

        if re.match(r'.*\|*monitor', line):
            if not line.startswith('show '):
                print('Can only monitor show commands.')
            else:
                while True:
                    line = line.partition('|')[0].rstrip()
                    try:
                        print(chr(27) + "[2J")
                        output = self.execute(line)
                        output += '\n\nHit Ctrl+C to abort'
                        print(output)

                        if re.findall(job_status, output):
                            print('Job is not running, stopping monitor.')
                            break

                        time.sleep(2)
                    except KeyboardInterrupt:
                        break
        else:
            print(self.execute(line), end='')

        readline.set_completer(self.old_completer)
        readline.write_history_file('history.txt')
