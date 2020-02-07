from typing import Optional, List
from cli.terminal import get_hline, terminal_size, print_hline, lrstrip


forbidden = ['confhash', 'oob_ip', 'infra_ip', 'site_id', 'port', 'dhcp_ip',
             'ztp_mac', 'platform']
job_fields = ['id', 'status', 'start_time', 'finish_time', 'function_name',
              'scheduled_by', 'exception']


def prettyprint_job(data: dict, command: str) -> str:
    """
    Prettyprinter for commands that start jobs
    """

    if type(data['data']) is str:
        res = '  ' + data['data'] + ' '
        if 'job_id' in data:
            res += '\n  Job ID: ' + str(data['job_id'])
        return res + '\n\n'
    return None


def prettyprint_jobs(data: dict, command: str) -> str:
    """
    Prettyprinter for jobs output
    """

    output = ''

    for field in job_fields:
        if field == 'id' or field == 'status':
            output += ('%5s\t| ' % field)
        else:
            output += '%25s\t| ' % field

    output += get_hline(newline=True)

    for job in data['data']['jobs']:
        for key in job:
            # Only print certain fields
            if key not in job_fields:
                continue

            # Don't print the backtrace
            if key == 'exception' and job['exception'] is not None:
                output += '%20s\t ' % job[key]['args'][0]
                continue

            # Variable column width
            if key == 'id' or key == 'status':
                output += '%5s\t ' % job[key]
            else:
                output += '%25s\t ' % job[key]
        output += '\n'
    return output


def prettyprint_command(data: dict, command: str) -> str:
    """
    Prettyprinter for commands
    """

    output = ''
    headers = []
    values = ''
    header_formatted = ''

    if command in data['data']:
        content = data['data'][command]
    else:
        content = data['data']

    try:
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
    except Exception:
        print(data)
        return 'Failed to parse output\n'

    return header_formatted + '\n' + '-' * width + '\n' + values + '\n'


def prettyprint_other(data: dict) -> str:
    """
    Prettyprinter for everything else
    """

    if 'data' in data and isinstance(data['data'], str):
        return '  ' + data['data'] + '\n'
    return ''


def prettyprint_groups(data: dict, name: str) -> str:
    """
    Prettyprint groups
    """

    output = ''

    for item in data['data'][name]:
        output += '  ' + item + ':\n'
        for line in data['data'][name][item]:
            output += '    ' + line + '\n'
        output += '\n'
    return output


def prettyprint_version(data: dict, name: str) -> str:
    """
    Prettyprint version output
    """

    output = ''

    for item in data['data']:
        output += '  ' + item + ':\t' + data['data'][item] + '\n'
    output += '\n'
    return output


def prettyprint_modifier(output, modifier):
    """
    Handle modifiers, grep etc
    """

    modified_output = ''
    command = lrstrip(modifier).split(' ')[0]
    args = ' '.join(lrstrip(modifier).split(' ')[1:])

    if lrstrip(command) == 'grep':
        for line in output.split('\n'):
            if args not in line:
                continue
            modified_output += line + '\n'
    modified_output += '\n'

    return modified_output


def prettyprint(data: dict, command: str, modifier: Optional[str] = '') -> str:
    """
    Prettyprint the JSON data we get back from the API
    """

    output = ''

    # A few commands need a little special treatment
    if command == 'job':
        command = 'jobs'
    if command == 'device':
        command = 'devices'

    if 'data' in data and 'jobs' in data['data']:
        output = prettyprint_jobs(data, command)
    elif 'job_id' in data:
        output = prettyprint_job(data, command)
    elif 'groups' in data['data']:
        output = prettyprint_groups(data, 'groups')
    elif 'version' in data['data']:
        output = prettyprint_version(data, 'version')
    elif 'data' in data and command in data['data']:
        output = prettyprint_command(data, command)
    else:
        output = prettyprint_other(data)

    if modifier != '':
        output = prettyprint_modifier(output, modifier)

    return output
