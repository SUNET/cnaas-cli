import fcntl
import termios
import struct

from typing import Optional, List


def terminal_size() -> tuple:
    """
    Get terminal width and height
    """

    packed_struct = struct.pack('HHHH', 0, 0, 0, 0)
    h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ,
                                                     packed_struct))
    return w, h


def prettyprint(data: dict, command: str) -> str:
    """
    Prettyprint the JSON data we get back from the API
    """

    headers = []
    values = ''
    header_formatted = ''
    forbidden = ['confhash', 'oob_ip', 'infra_ip', 'site_id', 'port']

    # A few commands need a littel special treatment
    if command == 'job':
        command = 'jobs'
    if command == 'device':
        command = 'devices'

    if type(data['data']) is str:
        res = data['data'] + ' '
        if 'job_id' in data:
            res += '\nJob ID: ' + str(data['job_id'])
        return res
    if command in data['data']:
        content = data['data'][command]
    else:
        content = data['data']

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

    (tty_width, tty_height) = terminal_size()

    return header_formatted + '\n' + '-' * tty_width + '\n' + values
