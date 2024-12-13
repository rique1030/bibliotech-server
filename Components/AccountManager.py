from flask import  request, jsonify
from .DatabaseHandlers.AccountDataParser import AccountDataParser
from .DatabaseHandlers.CrudHandler import CrudHandler
from .DatabaseQueries import ACCOUNT_HANDLER_QUERIES

class AccountManager:
    def __init__(self):
        self.acc = AccountDataParser()
        self.crud = CrudHandler()

    def signup(self):
        data = request.get_json()
        account = self.acc.parse_account_signup_data(data["account"])
        is_valid = self.validate_email_and_username(account)
        if not is_valid['success']: return {"success": False, "error": is_valid['error']}
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.INSERT_ACCOUNT, account)
    
    def validate_email_and_username(self, account):
        username = (account[0],)
        email = (account[2],)
        
        email_validation = self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNTS_BY_EMAIL, email , fetch=True)
        if email_validation['success'] and email_validation['data']:  return {"success": False, "error": "Email is already in use."}

        username_validation = self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNTS_BY_USERNAME, username, fetch=True)
        if  username_validation['success'] and username_validation['data']: return {"success": False, "error": "Username is already in use."}
        return {"success": True, "message": "Valid email and username."}

    def login(self):
        data = request.get_json()
        account = self.acc.parse_account_select_data(data["account"])
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNTS_BY_USERNAME_AND_PASSWORD,account, fetch=True)
    
    def update_accounts(self):
        data = request.get_json()
        accounts = self.acc.parse_account_update_datas(data["accounts"])
        return self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.UPDATE_ACCOUNTS, accounts)
    
    def delete_accounts(self):
        data = request.get_json()
        account_ids = self.acc.parse_account_delete_data(data["account_ids"])
        return self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.DELETE_ACCOUNT, account_ids)

    def get_accounts(self):
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNTS, fetch=True)
    
    def add_user_types(self):
        data = request.get_json()
        user_types = [(data,) for data in data["user_types"]]
        return self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.INSERT_ACCOUNT_TYPE, user_types)
    
    def get_user_types(self):
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNT_TYPES, fetch=True)
    
    def update_user_types(self):
        data = request.get_json()
        user_types = [(data["user_type"], data["user_type_id"]) for data in data["user_types"]]
        return self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.UPDATE_USER_TYPES, user_types)
    
    def delete_user_types(self):
        data = request.get_json()
        user_type_ids = [(data,) for data in data["user_type_ids"]]
        return self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.DELETE_ACCOUNT_TYPE, user_type_ids)
    
    def get_account_by_id(self, account_id):
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNT_BY_ID, (account_id,), fetch=True)