class NavDaily:
	def __init__(self, data):
		self.id = data["id"]
		self.nav = data["nav"]
		self.created_at = data["createdAt"]
		self.nav_date = data["navDate"]
		self.product_id = data["productId"]
