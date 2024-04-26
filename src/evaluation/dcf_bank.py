import statistics
from datetime import date, timedelta

from src.fireant.ReportType import ReportType
from src.fireant.service import get_history_quotes, get_full_financial_reports, get_fundamental
from src.evaluation.helper import percent_differences, cagr

MATURE_GROWTH_RATE = 0.035
EQUITY_COST_RATE = 0.15


def dcf_bank(ticker: str, year_count: int = 5):
	today = date.today()
	five_years_ago = today - timedelta(days=365 * year_count)

	price_in_5years = get_history_quotes(ticker, five_years_ago, today)

	# Standard Deviation of ticker
	stdev = statistics.stdev(percent_differences(price_in_5years))

	# Standard Deviation of VNINDEX
	vnindex_quotes = get_history_quotes('VNINDEX', five_years_ago, today)
	stdev_vnindex = statistics.stdev(percent_differences(vnindex_quotes))

	# Net income
	params = {
		'type': ReportType.INCOME.value,
		'year': today.year,
		'limit': year_count + 1,  # 6 years
		'quarter': 0
	}
	income_report = get_full_financial_reports(ticker, params)

	net_income_items = [report_item for report_item in income_report if report_item.id == 15]
	if len(net_income_items) == 0:
		raise ValueError("No net income items found")
	net_income_item = net_income_items[0]

	# owner's equity
	balance_report = get_full_financial_reports(ticker, {**params, 'type': ReportType.BALANCE.value})

	owners_equity_items = [item for item in balance_report if item.id == 308]
	if len(owners_equity_items) == 0:
		raise ValueError("No owners equity items found")
	owners_equity_item = owners_equity_items[0]

	# ROAEs
	roaes = [{
		'roae': net.value / statistics.mean([prev_oe.value, oe.value]),
		'year': oe.year
	} for net, prev_oe, oe in
		zip(net_income_item.values[1:], owners_equity_item.values[:-1], owners_equity_item.values[1:])]
	roe_mean = 0.8 * statistics.mean([y_roe.get('roae') for y_roe in roaes])

	# CAGR of owner's equity
	oe_init = owners_equity_item.values[0].value
	oe_final = owners_equity_item.values[-1].value
	owners_equity_cagr = cagr(oe_init, oe_final, year_count + 1)

	# Suppose in the next 6 years, this company has a declining owner's equity to MATURE_GROWTH_RATE
	cagr_carefully = owners_equity_cagr * 0.8
	cagr_step = (cagr_carefully - MATURE_GROWTH_RATE) / year_count

	def forecast_oe_growth_rate(i: int):
		growth_rate = cagr_carefully - (i * cagr_step)

		owners_equity = 0
		net_profit = 0
		net_profit_pv = 0
		if i == 0:
			owners_equity = (1 + growth_rate) * oe_final
			net_profit = statistics.mean([owners_equity, oe_final]) * roe_mean * (1 - EQUITY_COST_RATE)
			discount_rate = (1 + EQUITY_COST_RATE) ** (1 + i)
			net_profit_pv = net_profit / discount_rate

		return {
			'year': today.year + i,
			'growth_rate': growth_rate,
			'owners_equity': owners_equity,
			'net_profit': net_profit,
			'net_profit_pv': net_profit_pv,
		}

	owners_equity_forecast_carefully = [forecast_oe_growth_rate(i) for i in range(year_count + 1)]

	def forecast_profit(index: int):
		current = owners_equity_forecast_carefully[index]
		prev = owners_equity_forecast_carefully[index - 1]

		owners_equity = (1 + current.get('growth_rate')) * prev.get('owners_equity')
		net_profit = statistics.mean([owners_equity, prev.get('owners_equity')]) * roe_mean * (1 - EQUITY_COST_RATE)
		discount_rate = (1 + EQUITY_COST_RATE) ** index
		net_profit_pv = net_profit / discount_rate

		owners_equity_forecast_carefully[index] = {
			**current,
			'owners_equity': owners_equity,
			'net_profit': net_profit,
			'net_profit_pv': net_profit_pv,
		}

	for i in range(1, year_count + 1):
		forecast_profit(i)

	final_value = price_in_5years[0].price_close / price_in_5years[0].adj_ratio
	initial_value = price_in_5years[-1].price_close / price_in_5years[-1].adj_ratio
	adj_price_cagr = cagr(initial_value, final_value, year_count)

	fundamental = get_fundamental(ticker)

	total_net_profit_pv = sum([f.get('net_profit_pv') for f in owners_equity_forecast_carefully])
	company_value = total_net_profit_pv + oe_final
	forecast_price_per_share = company_value / fundamental.shares_outstanding

	return {
		'ticker': ticker,
		'standard_deviation': stdev,
		'standard_deviation_vnindex': stdev_vnindex,
		'price_adj_cagr': adj_price_cagr,
		'price_adj_latest': final_value,
		'price_forecast': forecast_price_per_share,
		'roaes': roaes,
		'roae_mean': statistics.mean([item['roae'] for item in roaes]),
		'owners_equity_forecast_carefully': owners_equity_forecast_carefully,
		'shares_outstanding': fundamental.shares_outstanding,
	}
