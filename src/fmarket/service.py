import http.client
import http.client
import json
import ssl
from datetime import date
from typing import List

from src.fmarket.FundID import FundID
from src.fmarket.NavDaily import NavDaily

# Disable SSL certificate verification
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

conn = http.client.HTTPSConnection("api.fmarket.vn", context=context)


def get_nav_history(ticker: FundID, start_date: date, end_date: date) -> List[NavDaily]:
	payload = {
		"isAllData": 1,
		"productId": ticker.value,
		"fromDate": start_date.strftime("%Y%m%d"),
		"toDate": end_date.strftime("%Y%m%d")
	}
	url = f"/res/product/get-nav-history"
	headers = {
		'Content-Type': 'application/json; charset=utf-8',
	}

	conn.request("POST", url, json.dumps(payload), headers=headers)

	response = conn.getresponse()

	if response.status == 200:
		response_data = json.loads(response.read())
		nav_history = response_data['data']

		return [NavDaily(nav) for nav in nav_history]
	else:
		raise ValueError("Cannot query fund history price")
