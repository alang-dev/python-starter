import json
import os
import unittest
from datetime import date
from typing import List
from unittest.mock import patch

from src.fireant.HistoryQuote import HistoryQuote
from src.fmarket.FundID import FundID
from src.fmarket.NavDaily import NavDaily
from src.fund.Allocation import Allocation
from src.fund.forecaster import forecast


class FundForecastTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		current_directory = os.path.dirname(__file__)

		dcds_file = open(os.path.join(current_directory, 'dcds.json'))
		cls.allocations: List[Allocation] = [Allocation(**json_dic) for json_dic in json.load(dcds_file)]
		dcds_file.close()

		tickers_file = open(os.path.join(current_directory, 'ticker_mock_price.json'))
		cls.tickers_latest_prices = {item["ticker"]: item["price"] for item in json.load(tickers_file)}
		tickers_file.close()

	def setUp(self):
		self.get_nav_history_mock = patch('src.fund.forecaster.get_nav_history').start()
		self.get_nav_history_mock.return_value = [
			NavDaily(
				{
					"id": 26097,
					"createdAt": 1712737344453,
					"nav": 74333.56,
					"navDate": "2024-04-10",
					"productId": 28
				}
			),
			NavDaily(
				{
					"id": 26118,
					"createdAt": 1712817576392,
					"nav": 73972.99,
					"navDate": "2024-04-11",
					"productId": 28
				}
			)
		]

		self.get_history_quotes_mock = patch('src.fund.forecaster.get_history_quotes').start()
		self.get_history_quotes_mock.side_effect = lambda *args: [HistoryQuote({
			'priceClose': self.tickers_latest_prices.get(args[0]),
			'symbol': args[0]
		})]

		self.date_mock = patch('src.fund.forecaster.date').start()
		self.date_mock.today.return_value = date.fromisoformat('2024-04-10')

	def test_forecast_fund_price(self):
		reported_date = date.fromisoformat("2023-03-31")
		actual = forecast(self.allocations, reported_date, FundID.DCDS)

		self.assertEqual(len(self.allocations), self.get_history_quotes_mock.call_count)
		self.assertEqual(1, self.get_nav_history_mock.call_count)

		self.assertEqual(71.6893913282321, actual)


if __name__ == '__main__':
	unittest.main()
