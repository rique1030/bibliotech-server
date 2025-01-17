from ..ContextManager import RequestContextManager

from ..config import *

if DEPLOYMENT_MODE == DeploymentMode.DEVELOPMENT:
    from mariadb import Error
else:
    from pymysql import Error

from json import dumps


class CrudHandler:
    def execyte_multiple_query(self, query, data, fetch = False):
        try:
            with RequestContextManager() as cursor:
                cursor.executemany(query, data)
                if fetch:
                    return {
                        "success": True,
                        "data": cursor.fetchall(),
                        "rows_affected": cursor.rowcount,
                        "lastrowid": cursor.lastrowid,
                        "message": f"{cursor.rowcount} rows affected.",
                    }
                return {
                    "success": True,
                    "data": None,
                    "rows_affected": cursor.rowcount,
                    "lastrowid": cursor.lastrowid,
                    "message": f"{cursor.rowcount} rows affected.",
                }
        except Error as err:
            return {
                "success": False,
                "data": None,
                "rows_affected": 0,
                "lastrowid": None,
                "message": f"An error occurred",
                "error": str(err),
            }

    def execute_query(self, query, data=None, fetch = False):
        try:
            with RequestContextManager() as cursor:
                cursor.execute(query, data)
                if fetch:
                    return {
                        "success": True,
                        "data": cursor.fetchall(),
                        "rows_affected": cursor.rowcount,
                        "lastrowid": cursor.lastrowid,
                        "message": f"{cursor.rowcount} rows affected.",
                    }
                return {
                    "success": True,
                    "data": None,
                    "rows_affected": cursor.rowcount,
                    "lastrowid": cursor.lastrowid,
                    "message": f"{cursor.rowcount} rows affected.",
                }
        except Error as err:
            print("execute_query error: ", err)
            return  {
                "success": False,
                "data": None,
                "rows_affected": 0,
                "lastrowid": None,
                "message": f"An error occurred",
                "error": str(err),
            }