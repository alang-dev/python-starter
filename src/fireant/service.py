import http.client
import http.client
import json
import ssl
import urllib.parse
from datetime import date
from typing import List

from src.fireant.HistoryQuote import HistoryQuote

# Disable SSL certificate verification
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

conn = http.client.HTTPSConnection("restv2.fireant.vn", context=context)
headers = {
	'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkdYdExONzViZlZQakdvNERWdjV4QkRITHpnSSIsImtpZCI6IkdYdExONzViZlZQakdvNERWdjV4QkRITHpnSSJ9.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmZpcmVhbnQudm4iLCJhdWQiOiJodHRwczovL2FjY291bnRzLmZpcmVhbnQudm4vcmVzb3VyY2VzIiwiZXhwIjoyMDA1NzQxOTk5LCJuYmYiOjE3MDU3NDE5OTksImNsaWVudF9pZCI6ImZpcmVhbnQudHJhZGVzdGF0aW9uIiwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsInJvbGVzIiwiZW1haWwiLCJhY2NvdW50cy1yZWFkIiwiYWNjb3VudHMtd3JpdGUiLCJvcmRlcnMtcmVhZCIsIm9yZGVycy13cml0ZSIsImNvbXBhbmllcy1yZWFkIiwiaW5kaXZpZHVhbHMtcmVhZCIsImZpbmFuY2UtcmVhZCIsInBvc3RzLXdyaXRlIiwicG9zdHMtcmVhZCIsInN5bWJvbHMtcmVhZCIsInVzZXItZGF0YS1yZWFkIiwidXNlci1kYXRhLXdyaXRlIiwidXNlcnMtcmVhZCIsInNlYXJjaCIsImFjYWRlbXktcmVhZCIsImFjYWRlbXktd3JpdGUiLCJibG9nLXJlYWQiLCJpbnZlc3RvcGVkaWEtcmVhZCJdLCJzdWIiOiJlNzY3N2JlMy1mYTUwLTRhYjEtYTg2MS1lMTgzODRiYjIzNGIiLCJhdXRoX3RpbWUiOjE3MDU3NDE5OTksImlkcCI6Ikdvb2dsZSIsIm5hbWUiOiJhbGFuZ2tpZW45NkBnbWFpbC5jb20iLCJzZWN1cml0eV9zdGFtcCI6ImE2ZDQ2OWQzLTNlYmItNGMyNy04NTk4LWZiNTEyMjI2NDhhMiIsImp0aSI6ImM3MWJmMjM4NWNjZmYzZmExOGIzNzBiYWY3NThlYjc1IiwiYW1yIjpbImV4dGVybmFsIl19.Y2oRlwBq9xX4dJWZ9E8Ue-FTATT9EW1I4f3OD6U9VZGfYQbN_xyPvC-x5SD3pVWFuVUYNqs6XSEakKC3fPBbTnXEwhN_WlV5RA0Eo20xhFEkNHIuIuGTGuhmdmY0E2Kmt5ZH18GLl1E1By2VkC8o7QCB8lHfS9f5nJJm3bto91eoVBNVl-vsJDwAr8d1CUSW2OJ34ClT3su7UEnhUJKz1Bl965hVpd4JbaHald1Y83uaYOlGKfsX1RtpAGZzjVgp5knC9GwKz8Li32fIrEPDYxit6bXOepuuwSg5Zsr6nGcRZc1MgPyd2kaRMagnF3ykInkn6zokUBIRjltf_gPGGg',
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
	print(f"Load ticker price {ticker}")
	conn.request("GET", url, headers=headers)
	response = conn.getresponse()

	if response.status == 200:
		data = json.loads(response.read())
		return [HistoryQuote(quote_data) for quote_data in data]
	else:
		raise ValueError("Cannot query stock history quote")
