import builtins
import unittest
from unittest.mock import patch, Mock

from src.decorators.log_time import log_time


@log_time
def say(name):
	return f'Hello, {name}'


@log_time(human_readable=True)
def done(name):
	return f'Hello, {name}'


class LogTimeTestCase(unittest.TestCase):
	def setUp(self):
		mock = Mock()
		mock.side_effect = print  # ensure actual print is called to capture its txt

		self.print_original = print

		builtins.print = mock
		self.print_mock = mock

	def tearDown(self):
		builtins.print = self.print_original

	@patch('src.decorators.log_time.time')
	def test_it_print_executed_time(self, time_mock):
		time_mock.time.side_effect = [0.2, 0.3]

		self.assertEqual(say('Kien'), 'Hello, Kien')

		self.print_mock.assert_called_with("'say' took 0.100000 seconds to execute.")

	@patch('src.decorators.log_time.time')
	def test_it_print_human_readable_executed_time(self, time_mock):
		time_mock.time.side_effect = [1, 201]

		self.assertEqual(done('Kien'), 'Hello, Kien')

		self.print_mock.assert_called_with("'done' took 0:03:20 to execute.")


if __name__ == '__main__':
	unittest.main()
