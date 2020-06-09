import re
import requests

from typing import Optional, List
from cli.parser import CliParser
from cli.prettyprint import prettyprint
from typing import Optional, List
from urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Rest():
    cli = CliParser('cnaas.yml')

    @classmethod
    def parse_args(cls, line: str, url: Optional[str] = '') -> tuple:
        """
        Parse arguments from command. Strip the first word, which is the
        command itself and then build a dict with arguments.

        """

        args = line.rstrip().split(' ')[1:]
        command = line.split(' ')[0]
        url = url + cls.cli.get_url(command)

        if command == 'job' and args == []:
            args = ['id', 'last']
        elif re.findall(r'(job|device)', command):
            if len(args) == 1 and re.match(r'[0-9]+', args[0]):
                num_arg = args[0]
                args = ['id', num_arg]

        # Make a dict of arguments and values
        args = dict(zip(args[::2], args[1::2]))
        default_args = cls.cli.get_attributes_default(command)

        # Make sure we use bool and not str
        for key in args:
            if args[key] == 'true':
                args[key] = True
            if args[key] == 'false':
                args[key] = False

        # Sometimes we want to add something to the end of an URL.
        new_args = dict()
        for key in args:
            pattern = re.compile(r'<%s?>' % key)

            if cls.cli.get_url_suffix(command, key):
                if any(args[key] == x for x in ['last', '-1', '0']):
                    args[key] = 's?sort=-id&per_page=1&page=1'
                    url += str(args[key])

                    print('Showing the last job...\n')
                else:
                    url += '/' + str(args[key])
            elif pattern.search(url):
                url = pattern.sub(str(args[key]), url)
            else:
                new_args[key] = args[key]

        for key in default_args:
            if key not in new_args:
                new_args[key] = default_args[key]

        return (url, new_args)

    @classmethod
    def rest_call(cls, method: str, command: str, token: str, url: str,
                  modifier: Optional[str] = '') -> str:

        (url, args) = cls.parse_args(command, url)

        command = command.split(' ')[0]
        headers = {'Authorization': 'Bearer ' + token}

        try:
            if method == 'GET':
                res = requests.get(url, headers=headers, json=args,
                                   verify=False)
            if method == 'POST':
                res = requests.post(url, headers=headers, json=args,
                                    verify=False)
            elif method == 'PUT':
                res = requests.put(url, headers=headers, json=args,
                                   verify=False)
            elif method == 'DELETE':
                res = requests.put(url, headers=headers, json=args,
                                   verify=False)

            if res.status_code != 200:
                return prettyprint(res.json(), command)

        except Exception as e:
            return 'Could not execute command\n\n'

        return prettyprint(res.json(), command, modifier=modifier)

    @classmethod
    def get(cls, command: str, token: str, url: str,
            modifier: Optional[str] = '') -> str:
        """
        GET method, call NMS with the right URL and arguments

        """

        return cls.rest_call('GET', command, token, url, modifier)

    @classmethod
    def post(cls, command: str, token: str, url: str,
             modifier: Optional[str] = '') -> str:
        """
        POST method, call NMS with the right URL and arguments

        """

        return cls.rest_call('POST', command, token, url, modifier)

    @classmethod
    def put(cls, command: str, token: str, url: str,
            modifier: Optional[str] = '') -> str:
        """
        PUT method, call NMS with the right URL and arguments

        """

        return cls.rest_call('PUT', command, token, url, modifier)

    @classmethod
    def delete(cls, command: str, token: str, url: str,
               modifier: Optional[str] = '') -> str:
        """
        DELETE method, call NMS with the right URL and arguments

        """

        return cls.rest_call('DELETE', command, token, url, modifier)
