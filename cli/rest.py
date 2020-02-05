import requests

from typing import Optional, List
from cli.parser import CliParser
from cli.prettyprint import prettyprint
from typing import Optional, List


class Rest():
    cli = CliParser('cnaas.yml')

    @classmethod
    def parse_args(cls, command: str, url: Optional[str] = '') -> tuple:
        """
        Parse arguments from command. Strip the first word, which is the
        command itself and then build a dict with arguments.

        """

        args = command.split(' ')[1:]
        command = command.split(' ')[0]

        if url == '':
            url = cls.cli.get_base_url() + cls.cli.get_url(command)
        else:
            url = url + cls.cli.get_url(command)

        # Make a dict of arguments and values
        args = dict(zip(args[::2], args[1::2]))

        # Make sure we use bool and not str
        for key in args:
            if args[key] == 'true':
                args[key] = True
            if args[key] == 'false':
                args[key] = False

        # Sometimes we want to add something to the end of an URL.
        new_args = dict()
        for key in args:
            if cls.cli.get_url_suffix(command, key):
                url += '/' + str(args[key])
            else:
                new_args[key] = args[key]

        return (url, new_args)

    @classmethod
    def get(cls, command: str, token: str, url: Optional[str] = '') -> str:
        """
        GET method, call NMS with the right URL and arguments

        """

        if url != '':
            (url, args) = cls.parse_args(command, url)
        else:
            (url, args) = cls.parse_args(command, cls.cli.get_base_url())

        command = command.split(' ')[0]
        headers = {'Authorization': 'Bearer ' + token}

        try:
            res = requests.get(url, headers=headers, json=args, verify=False)

            if res.status_code != 200:
                return 'Could execute command, missing arguments?\n'
        except Exception as e:
            return 'GET failed: ' + str(e)
        return prettyprint(res.json(), command)

    @classmethod
    def post(cls, command: str, token: str, url: Optional[str] = '') -> str:
        """
        POST method, call NMS with the right URL and arguments

        """

        if url != '':
            (url, args) = cls.parse_args(command, url)
        else:
            (url, args) = cls.parse_args(command, cls.cli.get_base_url())

        command = command.split(' ')[0]
        headers = {'Authorization': 'Bearer ' + token}

        try:
            res = requests.post(url, headers=headers, json=args, verify=False)

            if res.status_code != 200:
                return 'Failed to sync device(s): ' + str(res.content)
        except Exception as e:
            return 'POST failed: ' + str(e)
        return prettyprint(res.json(), command)

    @classmethod
    def delete(cls, command: str, token: str) -> str:
        """
        DELETE method, call NMS with the right URL and arguments

        """

        return "test string for delete"
