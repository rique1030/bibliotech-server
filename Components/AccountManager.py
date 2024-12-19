from flask import  request
from json import dumps
from .DatabaseHandlers.AccountDataParser import AccountDataParser
from .DatabaseHandlers.CrudHandler import CrudHandler
from .DatabaseQueries import ACCOUNT_HANDLER_QUERIES

class AccountManager:
    def __init__(self):
        self.acc = AccountDataParser()
        self.crud = CrudHandler()
        self.page_size = 15

    def fetch_accounts(self):
        data = request.get_json()
        starting_index = data["page"] * self.page_size
        search_filter, search_params = AccountDataParser.build_search_filter(self, data["filter"], data["search"])
        query = ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNTS.format(search_filter=search_filter)
        params = search_params + [self.page_size, starting_index]
        result = self.crud.execute_query(query, params, fetch=True)
        return result


    def signup(self):
        account = request.get_json()
        account = self.acc.parse_account_signup_data(account["account"])
        accounts = self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.INSERT_ACCOUNT, account)
        return accounts
    
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
        self.debug_print(data, "login")
        account = self.acc.parse_account_select_data(data["account"])
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNTS_BY_USERNAME_AND_PASSWORD,account, fetch=True)
    
    def update_accounts(self):
        data = request.get_json()
        accounts = self.acc.parse_account_update_datas(data["account"])
        return self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.UPDATE_ACCOUNTS, accounts)
    
    def delete_accounts(self):
        data = request.get_json()
        self.debug_print(data, "delete_accounts")
        account_ids = self.acc.parse_account_delete_data(data["account"])
        result = self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.DELETE_ACCOUNT, account_ids)
        self.debug_print(result, "delete_accounts")
        return  result

    def get_accounts(self):
        data = request.get_json()
        self.debug_print(data, "get_accounts")
        if len(data) < 1:
            return { "success": True, "data": [] }
        placeholders = ",".join(["%s"] * len(data))
        result = self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNT_BY_ID.format(placeholders=placeholders), data, fetch=True)
        print(result)
        return result
    
    def insert_user_types(self):
        data = request.get_json()
        self.debug_print(data, "insert_user_types")
        # user_types = [(d[0], d[1], d[2], d[3], d[4]) for d in data["account"]]
        user_types = []
        for d in data["account"]:
            if d[0] == None or d[0] == "":
                continue
            user_types.append((d[0], d[1], d[2], d[3], d[4]))
        return self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.INSERT_ACCOUNT_TYPE, user_types)
    
    def fetch_user_types(self):
        data = request.get_json()
        self.debug_print(data, "fetch_user_types")
        starting_index = data["page"] * self.page_size
        search_filter, search_params = AccountDataParser.build_search_filter(self, data["filter"], data["search"])
        query = ACCOUNT_HANDLER_QUERIES.FETCH_USER_TYPES.format(search_filter=search_filter)
        params = search_params + [self.page_size, starting_index]
        result = self.crud.execute_query(query, params, fetch=True)
        return result

    def get_user_types(self):
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNT_TYPES, fetch=True)

    def get_user_type_by_id(self):
        data = request.get_json()
        self.debug_print(data, "get_user_type_by_id")
        if len(data) < 1:
            return { "success": True, "data": [] }
        placeholders = ",".join(["%s"] * len(data))
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNT_TYPES_BY_ID.format(placeholders=placeholders), data, fetch=True)

    def update_user_types(self):
        data = request.get_json()
        self.debug_print(data, "update_user_types")
        user_types = [(d[1], d[2], d[3], d[4], d[5], d[0]) for d in data["account"]]
        return self.crud.execyte_multiple_query(ACCOUNT_HANDLER_QUERIES.UPDATE_USER_TYPES, user_types)
    
    def delete_user_types(self):
        data = request.get_json()
        self.debug_print(data, "get_user_type_by_id")
        if len(data) < 1:
            return { "success": True, "data": [] }
        placeholders = ",".join(["%s"] * len(data))
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.DELETE_ACCOUNT_TYPE.format(placeholders=placeholders), data)
    
    def get_account_by_id(self, account_id):
        return self.crud.execute_query(ACCOUNT_HANDLER_QUERIES.SELECT_ACCOUNT_BY_ID, (account_id,), fetch=True)
    
    def debug_print(self, data , function_name):
        print(f"Function: {function_name}")
        print(f"Data: {dumps(data)}")
