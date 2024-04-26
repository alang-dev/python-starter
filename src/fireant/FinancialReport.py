from src.fireant.FinancialReportValue import FinancialReportValue


class FinancialReport:
	def __init__(self, data: dict):
		self.id = data.get("id")
		self.name = data.get("name")
		self.parentID = data.get("parentID")
		self.expanded = data.get("expanded")
		self.level = data.get("level")
		self.field = data.get("field")
		self.values = [FinancialReportValue(v) for v in data.get("values")]
