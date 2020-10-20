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
        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            for attr in cmd.command.attributes:
                if attr.name != attribute:
                    continue
                if attr.mandatory is True:
                    return True
                else:
                    return False
        return None

    def get_attributes_default(self, command: str) -> list:
        """
        Return whether an attribute have an default value or not

        """
        attributes = dict()

        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            if cmd.command.attributes is None:
                return attributes
            for attr in cmd.command.attributes:
                if attr.default is not None:
                    attributes[attr.name] = attr.default

        return attributes

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

    def get_attributes_show(self, command: str) -> str:
        attributes = []

        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            if cmd.command.attributes is None:
                return attributes
            for attr in cmd.command.attributes:
                if attr.show:
                    attributes.append(attr.name)

        return attributes

    def get_attributes_no(self, command: str) -> str:
        attributes = []

        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            if cmd.command.attributes is None:
                return attributes
            for attr in cmd.command.attributes:
                if attr.delete:
                    attributes.append(attr.name)

        return attributes

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

    def get_use_put(self, command: str) -> list:
        """
        Return true if we should use PUT instead of POST

        """

        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            return cmd.command.use_put

        return False

    def get_not_show(self) -> list:
        """
        Return true if this command is a show command only

        """
        commands = []

        for cmd in self.cli.cli:
            if not cmd.command.show_only:
                commands.append(cmd.command.name)

        return commands

    def get_delete(self) -> list:
        commands = []

        for cmd in self.cli.cli:
            if cmd.command.delete:
                commands.append(cmd.command.name)

        return commands

    def get_show(self) -> list:
        """
        Return true if this command can do show

        """
        commands = []

        for cmd in self.cli.cli:
            if not cmd.command.no_show:
                commands.append(cmd.command.name)

        return commands

    def get_update(self) -> list:
        """
        Return true if this command can be updated

        """
        commands = []

        for cmd in self.cli.cli:
            if cmd.command.update:
                commands.append(cmd.command.name)

        return commands

    def get_url_suffix(self, command: str, attribute: str) -> bool:
        """
        Find out if an argument should be a suffix to the URL or not

        """

        for cmd in self.cli.cli:
            if cmd.command.name != command:
                continue
            if cmd.command.attributes is None:
                return None
            for attr in cmd.command.attributes:
                if attr.name != attribute:
                    continue
                return attr.url_suffix

        return None
