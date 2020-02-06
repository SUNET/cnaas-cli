import yaml

from cli.cli_struct import f_cli
from typing import Optional, List


class CliParser():
    def __init__(self, file) -> None:
        """
        Contructor.

        Retuens:

        """

        self.__yaml_read(file)

    def __yaml_read(self, file) -> None:
        """
        Parse the YAML file and create a Cli class
        """

        with open(file, 'r') as fd:
            self.json = yaml.safe_load(fd)
        self.cli = f_cli(**self.json)

    def get_commands(self) -> list:
        """
        Return a list of command names
        """

        return [x.command.name for x in self.cli.cli]

    def get_command_description(self, command: str) -> str:
        """
        Return descirption of a specific command
        """
        try:
            return [x.command.description for x in self.cli.cli if x.command.name
                    == command][0]
        except Exception:
            return ''

    def get_attributes(self, command: str) -> list:
        """
        Return attribute names for a command
        """

        cmd_attrs = []
        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            if cmd.command.attributes is None:
                return []
            for attr in cmd.command.attributes:
                cmd_attrs.append(attr.name)
        return cmd_attrs

    def get_mandatory(self, command: str, attribute: str) -> list:
        """
        Return whether an attribute is mandatory or not
        """

        mandatory = []
        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            for attr in cmd.command.attributes:
                if attr != attribute:
                    continue
                if attr.mandatory:
                    return True
                else:
                    return False
        return None

    def get_attribute_description(self, command: str, attribute: str) -> str:
        """
        Return descirption for an attribute
        """

        description = ''
        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            for attr in cmd.command.attributes:
                if attr.name != attribute:
                    continue
                description = attr.description
        return description

    def get_url(self, command: str) -> str:
        """
        Return URL
        """

        url = ''
        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            url = cmd.command.url
        return url

    def get_methods(self, command: str) -> list:
        """
        Return attribute names for a command
        """

        cmd_methods = []
        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            for method in cmd.command.methods:
                cmd_methods.append(method.name)
        return cmd_methods

    def get_base_url(self) -> str:
        """
        Return base URL
        """

        return self.cli.base_url

    def get_url_suffix(self, command: str, attribute: str) -> bool:
        """
        Find out if an argument should be a suffix to the URL or not
        """

        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            for attr in cmd.command.attributes:
                if attr.name != attribute:
                    continue
                return attr.url_suffix
        return None
