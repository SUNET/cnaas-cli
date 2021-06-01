import unittest
from cli.command import CliHandler
from cli.parser import CliParser


class CliTests(unittest.TestCase):
    def setUp(self):
        self.valid_commands = [
            'sync hostname test dry_run True force True',
            'show device id 123',
            'show job id 123',
            'device id 123 hostname test device_type test platform test'
        ]

        self.invalid_commands = [
            'device',
        ]

        self.help_commands = [
            'help devices'
        ]

        self.no_commands = [
            'no device id 9'
        ]

        self.c = CliHandler('http://localhost')
        self.p = CliParser('cnaas.yml')

    def tearDown(self):
        pass

    def test_01_valid_commands(self):
        for command in self.valid_commands:
            self.assertEqual(self.c.validate(command), True)

    def test_02_invalid_commands(self):
        for command in self.invalid_commands:
            self.assertEqual(self.c.validate(command), False)

    def test_03_help_commands(self):
        for command in self.help_commands:
            self.assertEqual(self.c.is_help(command), True)

    def test_04_invalid_help_commands(self):
        for command in self.invalid_commands:
            self.assertEqual(self.c.is_help(command), False)

    def test_05_no_commands(self):
        for command in self.no_commands:
            self.assertEqual(self.c.is_no(command), True)

    def test_06_invalid_no_commands(self):
        for command in self.invalid_commands:
            self.assertEqual(self.c.is_no(command), False)

    def test_07_parser_get_commands(self):
        self.assertNotEqual(self.p.get_commands(), [])

    def test_08_parser_get_command_description(self):
        self.assertNotEqual(self.p.get_command_description('device'), '')

    def test_09_parser_get_command_attributes(self):
        self.assertNotEqual(self.p.get_attributes('device'), '')

    def test_10_parser_get_mandatory_attributes(self):
        for attr in self.p.get_attributes('device'):
            mandatory = self.p.get_mandatory('device', attr)
            if attr == 'id':
                self.assertEqual(mandatory, True)
            if attr == 'hostname':
                self.assertEqual(mandatory, True)
            if attr == 'platform':
                self.assertEqual(mandatory, True)
            if attr == 'device_type':
                self.assertEqual(mandatory, True)

    def test_11_parser_get_attribute_description(self):
        for attr in self.p.get_attributes('device'):
            self.assertNotEqual(self.p.get_attribute_description('device',
                                                                 attr), '')

    def test_12_get_command_url(self):
        self.assertNotEqual(self.p.get_url('device'), '')

    def test_13_get_command_methods(self):
        methods = self.p.get_methods('device')
        self.assertNotEqual(methods, [])

    def test_14_get_url_suffix(self):
        suffix = self.p.get_url_suffix('job', 'id')
        self.assertNotEqual(suffix, '')
