from datetime import date, timedelta
from typing import List

from src.fireant.service import get_history_quotes
from src.fmarket.service import get_nav_history
from src.fmarket.FundID import FundID
from src.fund import Allocation


def forecast(allocations: List[Allocation], reported_date: date, ticker: FundID) -> float:
	"""
	Forecast fund NAV/certificate for next latest reported date
	:param allocations: list of Allocation from fund portfolio
	:param reported_date: the reported date of allocations
	:param ticker: fund ticker
	:return: forecast price
	"""
	if len(allocations) == 0:
		print('Allocation is empty.')
		return 0

	total_at_reported_date = 0
	fund_prices = get_nav_history(ticker, reported_date, date.today())

	if len(fund_prices) == 0:
		raise ValueError("Fund history price not found")
	price_at_reported_date: float = fund_prices[-1].nav

	total_at_latest_date = 0

	for alloc in allocations:
		total_at_reported_date += alloc.unit_price * alloc.quantity

		latest_unit_price = latest_stock_price(alloc.ticker)

		total_at_latest_date += latest_unit_price * alloc.quantity

	return total_at_latest_date * price_at_reported_date / total_at_reported_date


def latest_stock_price(ticker: str) -> float:
	today = date.today()
	back_to_2weeks = today - timedelta(days=14)

	quotes = get_history_quotes(ticker, back_to_2weeks, today)

	return quotes[0].price_close
