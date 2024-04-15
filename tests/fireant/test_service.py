import json
import os
import unittest
from datetime import date
from unittest.mock import patch, Mock, ANY

from src.fireant.service import get_history_quotes


class FireantServiceTest(unittest.TestCase):
	def setUp(self):
		self.https_connection = patch('src.fireant.service.HTTPSConnection').start()
		current_directory = os.path.dirname(__file__)

		with (open(os.path.join(current_directory, 'history_quote.json')) as f):
			self.history_quotes = json.dumps(json.load(f))

	def test_return_list_of_HistoryQuote(self):
		conn_mock = self.https_connection.return_value

		response_mock = Mock()
		response_mock.status = 200
		response_mock.read.return_value = self.history_quotes
		conn_mock.getresponse.return_value = response_mock

		ticker = 'ACB'
		start_date = date.fromisoformat('2024-01-01')
		end_date = date.fromisoformat('2024-01-04')
		actual_quotes = get_history_quotes(ticker, start_date, end_date)

		url = f"/symbols/{ticker}/historical-quotes?startDate={start_date.isoformat()}&endDate={end_date.isoformat()}&offset=0&limit=3"
		conn_mock.request.assert_called_once_with('GET', url, headers=ANY)

		self.assertEqual(len(actual_quotes), 1)
		self.assertIsInstance(actual_quotes[0].symbol, str)
		self.assertIsInstance(actual_quotes[0].price_close, float)
		self.assertIsInstance(actual_quotes[0].adj_ratio, float)

	def test_it_raises_error_when_status_is_not_200(self):
		conn_mock = self.https_connection.return_value

		response_mock = Mock()
		response_mock.status = 500
		conn_mock.getresponse.return_value = response_mock

		ticker = 'ACB'
		start_date = date.fromisoformat('2024-01-01')
		end_date = date.fromisoformat('2024-01-04')

		with self.assertRaisesRegex(ValueError, "Cannot query stock history quote"):
			get_history_quotes(ticker, start_date, end_date)


if __name__ == '__main__':
	unittest.main()
