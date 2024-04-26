from http.client import HTTPSConnection
import json
import os
import ssl
import urllib.parse
from datetime import date
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


@log_time
def get_history_quotes(ticker: str, start_date: date, end_date: date) -> List[HistoryQuote]:
	params = {
		'startDate': start_date,
		'endDate': end_date,
		'offset': 0,
		'limit': (end_date - start_date).days,
	}
	encoded_params = urllib.parse.urlencode(params)
	url = f"/symbols/{ticker}/historical-quotes?{encoded_params}"

	conn = get_connection()
	conn.request("GET", url, headers=build_headers())

	response = conn.getresponse()

	if response.status == 200:
		data = json.loads(response.read())
		return [HistoryQuote(quote_data) for quote_data in data]
	else:
		raise ValueError("Cannot query stock history quote")


@log_time
def get_full_financial_reports(ticker: str, params: dict) -> List[FinancialReport]:
	"""
	Retrieve full financial reports for a given ticker.
	:param ticker: The ticker symbol of the company.
	:param params: Additional parameters for the query.
	:return: [FinancialReport]
	"""
	url = f"/symbols/{ticker}/full-financial-reports?{urllib.parse.urlencode(params)}"

	conn = get_connection()
	conn.request("GET", url, headers=build_headers())

	response = conn.getresponse()

	if response.status == 200:
		data = json.loads(response.read())
		return [FinancialReport(report) for report in data]
	else:
		raise ValueError("Cannot query full financial reports")


def get_fundamental(ticker: str) -> FundamentalInfo:
	url = f"/symbols/{ticker}/fundamental"

	conn = get_connection()
	conn.request("GET", url, headers=build_headers())

	response = conn.getresponse()

	if response.status == 200:
		data = json.loads(response.read())
		return FundamentalInfo(data)
	else:
		raise ValueError("Cannot query full financial reports")
