from typing import Optional, List
from cli.terminal import print_hline, terminal_size


forbidden = ['confhash', 'oob_ip', 'infra_ip', 'site_id', 'port']
job_fields = ['id', 'status', 'start_time', 'finish_time', 'function_name',
              'scheduled_by', 'exception']


def prettyprint_job(data: dict, command: str) -> str:
    """
    Prettyprinter for commands that start jobs
    """

    if type(data['data']) is str:
        res = data['data'] + ' '
        if 'job_id' in data:
            res += '\nJob ID: ' + str(data['job_id'])
        return res + '\n'
    return None


def prettyprint_jobs(data: dict, command:str) -> str:
    """
    Prettyprinter for jobs output
    """

    for field in job_fields:
        if field == 'id' or field == 'status':
            print('%5s\t| ' % field, end='')
        else:
            print('%25s\t| ' % field, end='')

    print_hline(newline=True)

    for job in data['data']['jobs']:
        for key in job:
            # Only print certain fields
            if key not in job_fields:
                continue

            # Don't print the backtrace
            if key == 'exception' and job['exception'] is not None:
                print('%20s\t ' % job[key]['args'][0], end='')
                continue

            # Variable column width
            if key == 'id' or key == 'status':
                print('%5s\t ' % job[key], end='')
            else:
                print('%25s\t ' % job[key], end='')
        print('')
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

    # A few commands need a little special treatment
    if command == 'job':
        command = 'jobs'
    if command == 'device':
        command = 'devices'

    if 'data' in data and 'jobs' in data['data']:
        return prettyprint_jobs(data, command)
    elif 'job_id' in data:
        return prettyprint_job(data, command)
    elif 'data' in data and command in data['data']:
        return prettyprint_other(data, command)
