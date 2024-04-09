class Allocation:
	def __init__(self, ticker: str, unitPrice: float, quantity: int, percent: float):
		self.ticker = ticker
		self.unit_price = unitPrice
		self.quantity = quantity
		self.percent = percent

	def __str__(self):
		return f"Ticker: {self.ticker}, Unit Price: {self.unit_price}, Quantity: {self.quantity}, Percent: {self.percent}"
