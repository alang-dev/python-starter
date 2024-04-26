import json
import os
import unittest
from datetime import date
from typing import List
from unittest.mock import patch

from src.evaluation.dcf_bank import dcf_bank
from src.fireant.FinancialReport import FinancialReport
from src.fireant.FundamentalInfo import FundamentalInfo
from src.fireant.HistoryQuote import HistoryQuote
from src.fireant.ReportType import ReportType


def load_data(file_name: str, cls: type) -> List:
	current_directory = os.path.dirname(__file__)

	with open(os.path.join(current_directory, file_name)) as file:
		return [cls(json_dic) for json_dic in json.load(file)]


class DCFBankTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.history_quotes_acb: List[HistoryQuote] = load_data('history_quotes_acb.json', HistoryQuote)
		cls.history_quotes_vnindex: List[HistoryQuote] = load_data('history_quotes_vnindex.json', HistoryQuote)
		cls.balance_report_acb: List[FinancialReport] = load_data('balance_acb.json', FinancialReport)
		cls.income_report_acb: List[FinancialReport] = load_data('income_acb.json', FinancialReport)
		cls.fundamental_acb: FundamentalInfo = load_data('fundamental_acb.json', FundamentalInfo)[0]

	def setUp(self):
		self.date_mock = patch('src.evaluation.dcf_bank.date').start()
		self.date_mock.today.return_value = date.fromisoformat('2024-04-22')

		self.get_history_quotes_mock = patch('src.evaluation.dcf_bank.get_history_quotes').start()
		self.get_full_financial_reports_mock = patch('src.evaluation.dcf_bank.get_full_financial_reports').start()
		self.get_fundamental_mock = patch('src.evaluation.dcf_bank.get_fundamental').start()

	def test_bank_dcf_evaluation(self):
		self.get_fundamental_mock.return_value = self.fundamental_acb

		def get_history_quotes_mock(ticker: str, start_date: date, end_date: date):
			match ticker:
				case 'ACB':
					return self.history_quotes_acb
				case 'VNINDEX':
					return self.history_quotes_vnindex
				case _:
					return []

		self.get_history_quotes_mock.side_effect = get_history_quotes_mock

		def get_full_financial_reports_mock(ticker: str, param: dict):
			match param.get('type'):
				case ReportType.INCOME.value:
					return self.income_report_acb

				case ReportType.BALANCE.value:
					return self.balance_report_acb

				case _:
					return []

		self.get_full_financial_reports_mock.side_effect = get_full_financial_reports_mock

		actual = dcf_bank('ACB')

		expected = {
			'ticker': 'ACB',
			'standard_deviation': 0.018882390410026605,
			'standard_deviation_vnindex': 0.012651480062573063,
			'price_adj_cagr': 0.2308215216094398,
			'price_adj_latest': 26.8,
			'price_forecast': 36981.49280091905,
			'shares_outstanding': 3884050358,
			'roaes': [
				{'roae': 0.24639342456381244, 'year': 2019},
				{'roae': 0.24307530278094613, 'year': 2020},
				{'roae': 0.2390256853246544, 'year': 2021},
				{'roae': 0.26491677360537164, 'year': 2022},
				{'roae': 0.2479969028697823, 'year': 2023}
			],
			'roae_mean': 0.2482816178289134,
			'owners_equity_forecast_carefully': [
				{
					'growth_rate': 0.179843203558665,
					'net_profit': 13056826279367.9,
					'net_profit_pv': 11353761982059.045,
					'owners_equity': 83716908337823.7,
					'year': 2024
				},
				{
					'growth_rate': 0.15087456284693201,
					'net_profit': 15200285619956.04,
					'net_profit_pv': 13217639669526.992,
					'owners_equity': 96347660286189.55,
					'year': 2025
				},
				{
					'growth_rate': 0.121905922135199,
					'net_profit': 17258012580977.541,
					'net_profit_pv': 13049536923234.438,
					'owners_equity': 108093010658946.38,
					'year': 2026
				},
				{
					'growth_rate': 0.092937281423466,
					'net_profit': 19097534840063.438,
					'net_profit_pv': 12556939156777.145,
					'owners_equity': 118138881210466.58,
					'year': 2027
				},
				{
					'growth_rate': 0.063968640711733,
					'net_profit': 20583509863546.29,
					'net_profit_pv': 11768688570178.807,
					'owners_equity': 125696064856705.02,
					'year': 2028
				},
				{
					'growth_rate': 0.035,
					'net_profit': 21592830655212.98,
					'net_profit_pv': 10735453051007.623,
					'owners_equity': 130095427126689.69,
					'year': 2029
				}]
		}
		for k, v in expected.items():
			self.assertEqual(v, actual[k])


if __name__ == '__main__':
	unittest.main()
