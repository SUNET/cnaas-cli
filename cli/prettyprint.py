from typing import Optional, List
from cli.terminal import get_hline, terminal_size, print_hline, lrstrip


forbidden = ['confhash', 'oob_ip', 'infra_ip', 'site_id', 'port', 'dhcp_ip',
             'ztp_mac', 'platform']
job_fields = ['id', 'status', 'start_time', 'finish_time', 'function_name',
              'scheduled_by', 'exception']


def prettyprint_error(data: dict) -> str:
    """
    Print generic errors returned from the API.
    """

    error = 'Could not execute command\n'

    if 'message' in data:
        error += data['message']
    else:
        error += 'Unknown error'

    return '\n\033[91m%s\033[0m\n\n' % error


def prettyprint_device(data: dict) -> str:
    """
    Prettyprint a single device.
    """

    output = ''
    device_data = data['data']['devices'][0]

    output += '  %-30s %-30d\n' % ('ID:', device_data['id'])
    output += '  %-30s %-30s\n' % ('Hostname:', device_data['hostname'])
    output += '  %-30s %-30s\n' % ('Site iD:', device_data['site_id'])
    output += '  %-30s %-30s\n' % ('Description:', device_data['description'])
    output += '  %-30s %-30s\n' % ('Managemnt IP:', device_data['management_ip'])
    output += '  %-30s %-30s\n' % ('DHCP IP:', device_data['dhcp_ip'])
    output += '  %-30s %-30s\n' % ('Infra IP:', device_data['infra_ip'])
    output += '  %-30s %-30s\n' % ('OOP IP:', device_data['oob_ip'])
    output += '  %-30s %-30s\n' % ('Serial:', device_data['serial'])
    output += '  %-30s %-30s\n' % ('ZTP MAC:', device_data['ztp_mac'])
    output += '  %-30s %-30s\n' % ('Platform:', device_data['platform'])
    output += '  %-30s %-30s\n' % ('Vendor:', device_data['vendor'])
    output += '  %-30s %-30s\n' % ('Model:', device_data['model'])
    output += '  %-30s %-30s\n' % ('OS version:', device_data['os_version'])
    output += '  %-30s %-30s\n' % ('Hostname:', device_data['hostname'])
    output += '  %-30s %-30s\n' % ('Synchronized:', device_data['synchronized'])
    output += '  %-30s %-30s\n' % ('State:', device_data['state'])
    output += '  %-30s %-30s\n' % ('Device type:', device_data['device_type'])
    output += '  %-30s %-30s\n' % ('Configuration hash:', device_data['confhash'])
    output += '  %-30s %-30s\n' % ('Last seen:', device_data['last_seen'])
    output += '  %-30s %-30s\n' % ('Port:', device_data['port'])
    output += '\n'

    return output


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


def prettyprint_diff(diff: str) -> str:
    """
    Colorcode the diff

    """

    output = '\n'
    diff = diff.replace('\\n', '\n')

    for line in diff.split('\n'):
        if line.startswith('+'):
            output += '\033[92m %s\n' % line
        elif line.startswith('@@'):
            continue
        elif line.startswith('-'):
            output += '\033[91m %s\n' % line
        elif line.startswith('@'):
            output += '\033[93m %s\n' % line
        else:
            output += ' \033[0m%s\n' % line

    return output


def get_devices_data(data):
    """
    Aggregate diffs and get list of hostnames

    """

    devices = dict()
    diff = ''
    diffs = dict()

    devices = data['result']['devices']

    for device in devices:
        hostname = device
        failed = devices[device]['failed']
        reason = None

        for task in devices[device]['job_tasks']:
            if task['failed']:
                if task['result']:
                    reason = task['result']
            if task['diff'] is not None:
                diff = prettyprint_diff(lrstrip(task['diff']))

        if diff not in diffs:
            diffs[diff] = {
                'hostnames': [hostname],
                'failed': failed,
                'reason': reason
            }
        else:
            diffs[diff]['hostnames'].append(hostname)

    return diffs


def prettyprint_devices(data: dict) -> str:
    """
    Format outpu from devices

    """

    devices = get_devices_data(data['data']['jobs'][0])
    first_job = data['data']['jobs'][0]
    finished = first_job['finished_devices']

    output = '  Comment: %-20s\n' % first_job['comment']
    output += '  Finished devices: %-20s\n' % ', '.join(finished)

    for diff in devices:
        hostnames = devices[diff]['hostnames']
        failed = devices[diff]['failed']
        reason = devices[diff]['reason']

        if reason is not None:
            reason = '\033[91m %s\033[0m' % str(reason)

        output += '\n' + get_hline()
        output += '  Device(s): %s\n' % ', '.join(hostnames)
        output += '  Failed: %s\n' % str(failed)
        output += '  Reason: %s\n' % reason
        output += '  Diff: \n'
        output += diff

    return output


def prettyprint_jobs_single(data: dict) -> str:
    """
    Prettyprinter for single job output

    """

    output = ''
    job_data = data['data']['jobs'][0]
    result = 'None'
    exception = 'None'

    if job_data['exception'] is not None and 'message' in job_data['exception']:
        exception = job_data['exception']['message']
    if job_data['exception'] is None and job_data['result'] is not None:
        if 'message' in job_data['result']:
            result = job_data['result']['message']

    output += '  %-30s %-50d\n' % ('ID:', job_data['id'])
    output += '  %-30s %-50s\n' % ('Scheduled time:', job_data['scheduled_time'])
    output += '  %-30s %-50s\n' % ('Start time:', job_data['start_time'])
    output += '  %-30s %-30s\n' % ('Finish time: ', job_data['finish_time'])
    output += '  %-30s %-30s\n' % ('Scheduled by:', job_data['scheduled_by'])
    output += '  %-30s %-30s\n' % ('Comment:', job_data['comment'])
    output += '  %-30s %-30s\n' % ('Function name:', job_data['function_name'])
    output += '  %-30s %-30s\n' % ('Next job ID:', job_data['next_job_id'])
    output += '  %-30s %-30s\n' % ('Result:', lrstrip(result))
    output += '  %-30s %-30s\n' % ('Exception:', lrstrip(exception))

    if job_data['result'] is not None and 'devices' in job_data['result']:
        output += prettyprint_devices(data)

    output += '\n'

    return output


def prettyprint_jobs_all(data: dict) -> str:
    """
    Prettyprinter for all jobs output

    """

    output = ''
    jobs_data = data['data']['jobs']
    error = None
    jobs_data.reverse()

    for field in job_fields:
        if field == 'id' or field == 'status':
            output += '%5s\t| ' % field
        else:
            output += '%25s\t| ' % field

    output += '\n' + get_hline(newline=True)

    for job in jobs_data:
        for key in job:
            if key == 'result':
                if not job['result']:
                    continue
                if 'error' in job['result']:
                    error = job['result']['error']

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
    output += '\n'

    return output


def prettyprint_jobs(data: dict, command: str) -> str:
    """
    Prettyprinter for jobs output

    """

    nr_jobs = len(data['data']['jobs'])

    if nr_jobs > 1:
        return prettyprint_jobs_all(data)

    return prettyprint_jobs_single(data)


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

    return '  Failed to execute command.\n\n'


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


def prettyprint_firmware(data: dict, name: str) -> str:
    """
    Prettyprint files
    """

    output = ''

    for item in data['data']['files']:
        output += '  ' + item
        output += '\n'
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


def prettyprint_modifier(lines, modifier):
    """
    Handle modifiers, grep etc

    """

    output = ''
    command = lrstrip(modifier).split(' ')[0]
    args = ' '.join(lrstrip(modifier).split(' ')[1:])

    if lrstrip(command) == 'grep':
        for line in lines.split('\n'):
            if args not in line:
                continue
            output += line + '\n'
    output += '\n'

    return output


def prettyprint(data: dict, command: str, modifier: Optional[str] = '') -> str:
    """
    Prettyprint the JSON data we get back from the API

    """
    output = ''

    # A few commands need a little special treatment
    if command == 'job':
        command = 'jobs'

    if 'data' in data and 'jobs' in data['data']:
        output = prettyprint_jobs(data, command)
    elif 'data' in data and 'files' in data['data']:
        output = prettyprint_firmware(data, command)
    elif 'job_id' in data:
        output = prettyprint_job(data, command)
    elif 'data' in data and 'groups' in data['data']:
        output = prettyprint_groups(data, 'groups')
    elif 'data' in data and 'version' in data['data']:
        output = prettyprint_version(data, 'version')
    elif 'data' in data and command == 'device':
        output = prettyprint_device(data)
    elif 'data' in data and command in data['data']:
        output = prettyprint_command(data, command)
    elif 'status' in data and data['status'] == 'error':
        output = prettyprint_error(data)
    else:
        output = prettyprint_other(data)

    if modifier != '':
        output = prettyprint_modifier(output, modifier)

    return output
