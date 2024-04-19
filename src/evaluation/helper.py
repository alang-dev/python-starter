from typing import List

from src.fireant.HistoryQuote import HistoryQuote


def cagr(initial_value, final_value, periods):
	return ((final_value / initial_value) ** (1 / periods)) - 1


def percent_differences(history_quotes: List[HistoryQuote]) -> list:
	def adj_price(quote):
		return quote.price_close / quote.adj_ratio

	return [adj_price(left) / adj_price(right) - 1 for left, right in zip(history_quotes, history_quotes[1:])]
