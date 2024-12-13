class AccountDataParser:
		
	def parse_account_signup_data(self, accounts):
		acc = (
				accounts['username'], 
				accounts['password'], 
				accounts['email'], 
				accounts['user_type_id']
		)
		return acc
					
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
					account['username'], 
					account['password'], 
					account['email'], 
					account['user_type_id'], 
					account['id']
				)
			)
		return acc
	
	def parse_account_delete_data(self, account_ids):
		acc = [
			(account_id,) for account_id in account_ids
			]
		return acc
	