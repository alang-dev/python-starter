import json
import os
import ssl
import urllib.parse
from datetime import date
from http.client import HTTPSConnection
from typing import List

from src.decorators.log_time import log_time
from src.fireant.FinancialReport import FinancialReport
from src.fireant.FundamentalInfo import FundamentalInfo
from src.fireant.HistoryQuote import HistoryQuote


def get_connection() -> HTTPSConnection:
	# Disable SSL certificate verification
	context = ssl.create_default_context()
	context.check_hostname = False
	context.verify_mode = ssl.CERT_NONE

	return HTTPSConnection("restv2.fireant.vn", context=context)


def build_headers() -> dict:
	token = os.getenv('FIREANT_TOKEN')
	return {
		'authorization': f'Bearer {token}',
	}


def get_history_quotes(ticker: str, start_date: date, end_date: date) -> List[HistoryQuote]:
	params = {
		'startDate': start_date,
		'endDate': end_date,
		'offset': 0,
		'limit': (end_date - start_date).days,
	}
	encoded_params = urllib.parse.urlencode(params)
	url = f"/symbols/{ticker}/historical-quotes?{encoded_params}"

	data = send_get(url)
	return [HistoryQuote(report) for report in data]


def get_full_financial_reports(ticker: str, params: dict) -> List[FinancialReport]:
	"""
	Retrieve full financial reports for a given ticker.
	:param ticker: The ticker symbol of the company.
	:param params: Additional parameters for the query.
	:return: [FinancialReport]
	"""
	url = f"/symbols/{ticker}/full-financial-reports?{urllib.parse.urlencode(params)}"
	data = send_get(url)
	return [FinancialReport(report) for report in data]


def get_fundamental(ticker: str) -> FundamentalInfo:
	url = f"/symbols/{ticker}/fundamental"
	dict_data = send_get(url)

	return FundamentalInfo(dict_data)


@log_time
def send_get(url: str, err_msg: str = None) -> dict:
	conn = get_connection()

	try:
		conn.request("GET", url, headers=build_headers())

		response = conn.getresponse()

		if response.status == 200:
			result = json.loads(response.read())
		else:
			raise ValueError(f"[{response.status}]: Send request fail" if err_msg is None else err_msg)
	finally:
		conn.close()

	return result
