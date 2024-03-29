import sys
import getopt
import requests

from typing import Optional

from cli.terminal import get_hline, lrstrip, terminal_size


def ids_to_hostnames() -> dict:
    """
    Return a dict of IDs and hostnames.
    """

    devices: dict = {}

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:t:')
    except getopt.GetoptError:
        return devices

    for opt, arg in opts:
        if opt == '-u':
            url = arg
        if opt == '-t':
            token = arg
    headers = {'Authorization': 'Bearer ' + token}
    url = url + '/devices'

    res = requests.get(url,
                       headers=headers,
                       verify=False)

    if 'data' not in res.json():
        return devices

    for device in res.json()['data']['devices']:
        devices[device['id']] = device['hostname']

    return devices


def prettyprint_error(data: dict) -> str:
    """
    Print generic errors returned from the API.
    """

    error = 'Could not execute command\n'

    if 'message' in data:
        if type(data['message']) == list:
            error += ', '.join(data['message'])
        elif type(data['message']) == str:
            error += data['message']
    else:
        error += 'Unknown error'

    return '\n\033[91m%s\033[0m\n\n' % error


def prettyprint_device(data: dict) -> str:
    """
    Prettyprint a single device.
    """

    output = ''

    if 'devices' in data['data']:
        device_data = data['data']['devices'][0]
    elif 'updated_device' in data['data']:
        device_data = data['data']['updated_device']
    elif 'deleted_device' in data['data']:
        device_data = data['data']['deleted_device']
    elif 'added_device' in data['data']:
        device_data = data['data']['added_device']
    else:
        'Could not parse response from API.'

    output += '  %-30s %-30d\n' % ('ID:', device_data['id'])
    output += '  %-30s %-30s\n' % ('Hostname:', device_data['hostname'])
    output += '  %-30s %-30s\n' % ('Site iD:', device_data['site_id'])
    output += '  %-30s %-30s\n' % ('Description:', device_data['description'])
    output += '  %-30s %-30s\n' % ('Managemnt IP:',
                                   device_data['management_ip'])
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
    output += '  %-30s %-30s\n' % ('Synchronized:',
                                   device_data['synchronized'])
    output += '  %-30s %-30s\n' % ('State:', device_data['state'])
    output += '  %-30s %-30s\n' % ('Device type:', device_data['device_type'])
    output += '  %-30s %-30s\n' % ('Configuration hash:',
                                   device_data['confhash'])
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
    if job_data['status'] == 'EXCEPTION' and job_data['result'] is not None and 'error' in job_data['result']:
        exception = '\033[91m%s\033[0m' % job_data['result']['error']
    if job_data['exception'] is None and job_data['result'] is not None:
        if 'message' in job_data['result']:
            result = job_data['result']['message']

    output += '  %-30s %-50d\n' % ('ID:', job_data['id'])
    output += '  %-30s %-50s\n' % ('Status:', job_data['status'])
    output += '  %-30s %-50s\n' % ('Scheduled time:',
                                   job_data['scheduled_time'])
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


def prettyprint_jobs_all(data: dict, modifier: str) -> str:
    """
    Prettyprinter for all jobs output

    """
    if 'detailed' in modifier:
        job_fields = ['id', 'status', 'scheduled_time', 'start_time',
                      'finish_time', 'function_name', 'scheduled_by',
                      'comment', 'ticket_ref', 'next_job_id', 'next_job',
                      'change_score',
                      'exception']
    else:
        job_fields = ['id', 'status', 'start_time', 'finish_time',
                      'function_name', 'scheduled_by', 'exception']

    output = ''
    jobs_data = data['data']['jobs']
    error = None
    jobs_data.reverse()

    for field in job_fields:
        if field == 'id':
            output += ' %-10s | ' % 'ID'
        elif field == 'status':
            output += ' %-10s | ' % 'Status'
        else:
            field = field.replace('_', ' ')
            output += ' %-30s | ' % field.capitalize()

    output += '\n' + get_hline(newline=True)

    for job in jobs_data:
        for key in job:
            if key == 'result':
                if not job['result']:
                    continue
                if 'error' in job['result']:
                    if type(job['result']) == str:
                        error = job['result']
                    else:
                        error = job['result']['error']

            # Only print certain fields
            if key not in job_fields:
                continue

            # Don't print the backtrace
            if key == 'exception' and job['exception'] is not None:
                output += ' %-30s | ' % job[key]['args'][0]
                continue

            # Variable column width
            if key == 'id' or key == 'status':
                output += ' %-10s | ' % job[key]
            else:
                output += ' %-30s | ' % job[key]
        output += '\n'
    output += '\n'

    return output


def prettyprint_jobs(data: dict, command: str, modifier) -> str:
    """
    Prettyprinter for jobs output

    """

    nr_jobs = len(data['data']['jobs'])

    if nr_jobs > 1:
        return prettyprint_jobs_all(data, modifier)

    return prettyprint_jobs_single(data)


def prettyprint_command(data: dict, command: str,
                        modifier: Optional[str] = None) -> str:
    """
    Prettyprinter for commands

    """

    forbidden = ['confhash', 'oob_ip', 'infra_ip', 'port', 'dhcp_ip',
                 'ztp_mac', 'platform', 'serial', 'last_seen', 'esi_mac']

    output = ''
    headers = []
    values = ''
    header_formatted = ''
    id_mapping = None

    if command in data['data']:
        content = data['data'][command]
    else:
        content = data['data']

    if 'detailed' in modifier:
        forbidden = []

    if command == 'linknets' or command == 'mgmtdomains':
        id_mapping = ids_to_hostnames()
    try:
        for row in content:
            for key in row:
                if key in forbidden:
                    continue
                if key not in headers:
                    headers.append(key)
                if key == 'id':
                    values += ' %-5s |' % str(row[key])
                elif key == 'management_ip':
                    values += ' %-16s |' % str(row[key])
                elif key == 'model':
                    values += ' %-20s |' % str(row[key])
                elif key == 'hostname':
                    values += ' %-20s |' % str(row[key])
                elif key == 'last_seen':
                    values += ' %-30s |' % str(row[key])
                elif key == 'os_version':
                    values += ' %-30s |' % str(row[key])
                elif key == 'device_a_id' or key == 'device_b_id':
                    if command == 'linknets' or command == 'mgmtdomains':
                        if row[key] in id_mapping:
                            values += ' %-20s |' % str(id_mapping[row[key]])
                else:
                    values += ' %-15s |' % str(row[key])
            values += '\n'

        for header in headers:
            if header == 'id':
                header_formatted += ' %-5s |' % 'ID'
            elif header == 'management_ip':
                header_formatted += ' %-16s |' % 'Management IP'
            elif header == 'model':
                header_formatted += ' %-20s |' % 'Model'
            elif header == 'hostname':
                header_formatted += ' %-20s |' % 'Hostname'
            elif header == 'last_seen':
                header_formatted += ' %-30s |' % 'Last seen'
            elif header == 'os_version':
                header_formatted += ' %-30s |' % 'OS version'
            elif header == 'device_a_id':
                header_formatted += ' %-20s |' % 'Device a id'
            elif header == 'device_b_id':
                header_formatted += ' %-20s |' % 'Device b id'
            else:
                header = header.replace('_', ' ')
                header_formatted += ' %-15s |' % str(header.capitalize())
    except Exception:
        print(data)
        return('Failed to parse output\n')

    values = values.replace('\\n', '\n')
    width, height = terminal_size()

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
    else:
        output = lines

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
        output = prettyprint_jobs(data, command, modifier)
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
        output = prettyprint_command(data, command, modifier)
    elif 'status' in data and data['status'] == 'error':
        output = prettyprint_error(data)
    else:
        output = prettyprint_other(data)

    if modifier != '':
        output = prettyprint_modifier(output, modifier)

    return output
