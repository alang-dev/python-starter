class FinancialReportValue:
	def __init__(self, data):
		self.period = data.get("period")
		self.year = data.get("year")
		self.quarter = data.get("quarter")
		self.value = data.get("value")
