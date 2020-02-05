from typing import Optional, List
from cli.terminal import print_hline, terminal_size


forbidden = ['confhash', 'oob_ip', 'infra_ip', 'site_id', 'port']


def preettyprint_jobs(data: dict) -> str:
    """
    Prettyprinter for jobs
    """

    if type(data['data']) is str:
        res = data['data'] + ' '
        if 'job_id' in data:
            res += '\nJob ID: ' + str(data['job_id'])
        return res
    return ''


def prettyprint_other(data: dict, command: str) -> str:
    """
    Prettyprinter for everything else
    """

    headers = []
    values = ''
    header_formatted = ''

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

    width, height = terminal_size()

    return header_formatted + '\n' + '-' * width + '\n' + values


def prettyprint(data: dict, command: str) -> str:
    """
    Prettyprint the JSON data we get back from the API
    """

    # A few commands need a littel special treatment
    if command == 'job':
        command = 'jobs'
        return preettyprint_jobs(data)
    if command == 'device':
        command = 'devices'

    return prettyprint_other(data, command)
