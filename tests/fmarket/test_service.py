import json
import random
import unittest
from datetime import date
from unittest.mock import patch, Mock

from faker import Faker

from src.fmarket.FundID import FundID
from src.fmarket.NavDaily import NavDaily
from src.fmarket.service import get_nav_history

fake = Faker()


class FmarketServiceTest(unittest.TestCase):
	def setUp(self):
		self.https_connection = patch('src.fmarket.service.HTTPSConnection').start()

	def test_get_nav_success(self):
		conn_instance = self.https_connection.return_value

		response_mock = Mock()
		response_mock.status = 200

		nav_item = {
			"id": fake.uuid4(),
			"nav": random.uniform(100, 1000),
			"createdAt": fake.date_time_this_year().isoformat(),
			"navDate": fake.date_time_this_month().isoformat(),
			"productId": fake.random_number(digits=1)
		}
		response_mock.read.return_value = json.dumps({
			'data': [nav_item]
		})
		conn_instance.getresponse.return_value = response_mock

		start = date.fromisoformat('2024-04-01')
		end = date.fromisoformat('2024-04-02')
		actual = get_nav_history(FundID.DCDS, start, end)

		self.assertEqual(len(actual), 1)

		expected_nav = NavDaily(nav_item)
		self.assertEqual(vars(actual[0]), vars(expected_nav))

	def test_get_nav_throw_error(self):
		conn_instance = self.https_connection.return_value

		response_mock = Mock()
		response_mock.status = 400
		conn_instance.getresponse.return_value = response_mock

		with self.assertRaisesRegex(ValueError, "Cannot query fund history price"):
			start = date.fromisoformat('2024-04-01')
			end = date.fromisoformat('2024-04-02')
			get_nav_history(FundID.DCDS, start, end)


if __name__ == '__main__':
	unittest.main()
