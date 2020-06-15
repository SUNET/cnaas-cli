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

        idx = 0
        new_args = dict()
        args_dict = dict()

        url = url + cls.cli.get_url(command)
        args = line.rstrip().split(' ')[1:]
        command = line.split(' ')[0]
        default_args = cls.cli.get_attributes_default(command)

        # If we have a job command and an empty list of arguments, set
        # the job ID to last. By doing this we will get the last job.
        #
        # Also, if we only and an ID, insert the argument keyword 'id'
        # before it to build a correct set of arguments.
        if command == 'job' and args == []:
            args = ['id', 'last']
        elif re.findall(r'(job|device)', command):
            if len(args) == 1 and re.match(r'[0-9]+', args[0]):
                num_arg = args[0]
                args = ['id', num_arg]

        # We also have to figure out if we have arguments without
        # values, then we should get the default value from the
        # specification and use that.
        for idx in range(0, len(args)):
            arg = args[idx]

            try:
                if arg in default_args:
                    if args[idx + 1] in default_args:
                        new_args[arg] = default_args[arg]
                    else:
                        new_args[arg] = args[idx + 1]
                        idx = idx + 1
            except IndexError:
                new_args[arg] = default_args[arg]

        # Sometimes we want to add something to the end of an URL, for
        # example if we have the argument 'last' for a job, we should
        # append something to the URL.
        for key in args_dict:
            pattern = re.compile(r'<%s?>' % key)

            if args_dict[key] == 'true':
                args_dict[key] = True
            if args_dict[key] == 'false':
                args_dict[key] = False

            if cls.cli.get_url_suffix(command, key):
                if any(args_dict[key] == x for x in ['last', '-1', '0']):
                    args_dict[key] = 's?sort=-id&per_page=1&page=1'
                    url += str(args_dict[key])

                    print('Showing the last job...\n')
                else:
                    url += '/' + str(args_dict[key])
            elif pattern.search(url):
                url = pattern.sub(str(args_dict[key]), url)
            else:
                new_args[key] = args_dict[key]

        return (url, new_args)

    @classmethod
    def rest_call(cls, method: str, command: str, token: str, url: str,
                  modifier: Optional[str] = '') -> str:

        (url, args) = cls.parse_args(command, url)

        print(args)

        command = command.split(' ')[0]
        headers = {'Authorization': 'Bearer ' + token}

        try:
            if method == 'GET':
                res = requests.get(url, headers=headers, json=args,
                                   verify=False)
            elif method == 'POST':
                res = requests.post(url, headers=headers, json=args,
                                    verify=False)
            elif method == 'PUT':
                res = requests.put(url, headers=headers, json=args,
                                   verify=False)
            elif method == 'DELETE':
                res = requests.put(url, headers=headers, json=args,
                                   verify=False)
            else:
                return 'Unknown REST method!'

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
