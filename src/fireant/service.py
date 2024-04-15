from http.client import HTTPSConnection
import json
import os
import ssl
import urllib.parse
from datetime import date
from typing import List

from src.fireant.HistoryQuote import HistoryQuote

# Disable SSL certificate verification
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


def get_history_quotes(ticker: str, start_date: date, end_date: date) -> List[HistoryQuote]:
	conn = HTTPSConnection("restv2.fireant.vn", context=context)
	token = os.getenv('FIREANT_TOKEN')
	headers = {
		'authorization': f'Bearer {token}',
	}

	params = {
		'startDate': start_date,
		'endDate': end_date,
		'offset': 0,
		'limit': (end_date - start_date).days,
	}
	encoded_params = urllib.parse.urlencode(params)
	url = f"/symbols/{ticker}/historical-quotes?{encoded_params}"
	print(f"Load ticker price {ticker}")
	conn.request("GET", url, headers=headers)
	response = conn.getresponse()

	if response.status == 200:
		data = json.loads(response.read())
		return [HistoryQuote(quote_data) for quote_data in data]
	else:
		raise ValueError("Cannot query stock history quote")
