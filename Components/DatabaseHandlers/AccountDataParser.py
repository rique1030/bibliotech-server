class AccountDataParser:
	def build_search_filter(self, filter_term, search_term):
		print(f"Filter Term: {filter_term}, Search Term: {search_term}")
		if not search_term or not filter_term:
			return "", []
		return f"WHERE {filter_term} LIKE %s", [f"%{search_term}%"]
	
	def parse_account_signup_data(self, accounts):
		acc = []
		for account in accounts:
			if account[0] == "":
				continue
			acc.append(
				(account[0], account[1], account[2], account[3])
			)
		return acc
		# acc = (
		# 		accounts['username'], 
		# 		accounts['password'], 
		# 		accounts['email'], 
		# 		accounts['user_type_id']
		# )
		# return acc
					
	def parse_account_select_data(self, account):
		acc = (
				account['email'], 
				account['password'], 
		)
		return acc

	def parse_account_update_datas(self, accounts):
		acc = []
		for account in accounts:
			acc.append(
				(
					account[1], 
					account[2], 
					account[3], 
					account[4], 
					account[0]
				)
			)
		return acc
	
	def parse_account_delete_data(self, account_ids):
		acc = [
			(account_id,) for account_id in account_ids
			]
		return acc
	