import requests

from model import Cli


class Rest():
    cli = Cli('cnaas.yml')

    def terminal_size():
        import fcntl, termios, struct
        h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
        return w, h

    @classmethod
    def prettyprint(cls, data, command):
        headers = []
        values = ''
        header_formatted = ''
        forbidden = ['confhash', 'oob_ip', 'infra_ip', 'site_id', 'port']

        if command == 'job':
            command = 'jobs'

        if type(data['data']) is str:
            res = data['data'] + ' '
            if 'job_id' in data:
                res += '\nJob ID: ' + str(data['job_id'])
            return res
        content = data['data'][command]
        for row in content:
            for key in row:
                if key in forbidden:
                    continue
                if key not in headers:
                    headers.append(key)
                values += ' %8s\t|' % str(row[key])
            values += '\n'
        for header in headers:
            header_formatted += ' %8s\t|' % str(header)

        values = values.replace('\\n', '\n')

        (tty_width, tty_height) = cls.terminal_size()

        return header_formatted + '\n' + '-' * tty_width + '\n' + values

    @classmethod
    def get(cls, command, token):
        args = command.split(' ')[1:]
        command = command.split(' ')[0]
        headers = {'Authorization': 'Bearer ' + token}
        url = cls.cli.get_base_url() + cls.cli.get_url(command)

        try:
            args = dict(zip(args[::2], args[1::2]))
            for key in args:
                if args[key] == 'true':
                    args[key] = True
                if args[key] == 'false':
                    args[key] = False
        except Exception:
            return 'Invalid list of arguments'

        new_args = dict()
        for key in args:
            if cls.cli.get_url_suffix(command, key):
                url += '/' + str(args[key])
            else:
                new_args[key] = args[key]

        res = requests.get(url, headers=headers, json=new_args)

        if res.status_code != 200:
            return 'Could not connect to NMS on ' + url
        return cls.prettyprint(res.json(), command)

    @classmethod
    def post(cls, command, token):
        args = command.split(' ')[1:]
        command = command.split(' ')[0]
        headers = {'Authorization': 'Bearer ' + token}
        url = cls.cli.get_base_url() + cls.cli.get_url(command)

        try:
            args = dict(zip(args[::2], args[1::2]))
            for key in args:
                if args[key] == 'true':
                    args[key] = True
                if args[key] == 'false':
                    args[key] = False
        except Exception:
            return 'Invalid list of arguments'

        new_args = dict()
        for key in args:
            if cls.cli.get_url_suffix(command, key):
                url += '/' + str(args[key])
            else:
                new_args[key] = args[key]
        res = requests.post(url, headers=headers, json=new_args)

        if res.status_code != 200:
            return 'Failed to sync device(s): ' + str(res.content)

        return cls.prettyprint(res.json(), command)

    @classmethod
    def delete(cls, command, token):
        return "test string for delete"
