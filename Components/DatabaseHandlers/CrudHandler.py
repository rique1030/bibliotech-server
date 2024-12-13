from ..ContextManager import RequestContextManager
from mariadb import Error


class CrudHandler:
    def execyte_multiple_query(self, query, data, fetch = False):
        try:
            with RequestContextManager() as cursor:
                cursor.executemany(query, data)
                if fetch:
                    return {"success": True, "data": cursor.fetchall()}
                return {"success": True, "message": f"{cursor.rowcount} rows affected."}
        except Error as err:
            return {"success": False, "message": f"Error: {err}"}

    def execute_query(self, query, data=None, fetch = False):
        try:
            with RequestContextManager() as cursor:
                cursor.execute(query, data)
                if fetch:
                    return {"success": True, "data": cursor.fetchall()}
                return {"success": True, "message": f"{cursor.rowcount} rows affected."}
        except Error as err:
            print("execute_query error: ", err)
            return {"success": False, "message": f"Error: {err}" }