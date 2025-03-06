from datetime import datetime
import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.ImageManager import ImageManager
from Components.queries.query_helper import QueryHelper
import pymysql


class BaseQuery:

    def __init__(self,
                 session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.query_helper = QueryHelper(session_factory)
        self.image_helper = ImageManager()
        # ? file paths
        self.storage_path = os.path.join(os.path.dirname(__file__),
                                         "../../storage")
        self.book_cover_path = os.path.join(self.storage_path, "images",
                                            "book_covers")
        self.user_photos_path = os.path.join(self.storage_path, "images",
                                             "user_photos")
        self.qr_code_path = os.path.join(self.storage_path, "qr-codes")

        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(self.book_cover_path, exist_ok=True)
        os.makedirs(self.user_photos_path, exist_ok=True)
        os.makedirs(self.qr_code_path, exist_ok=True)

    async def execute_query(self, operation, *args, **kwargs):
        async with self.session_factory() as session:
            try:
                result = await operation(session, *args, **kwargs)
                await session.commit()
                if "data" not in result or "message" not in result:
                    print(result)
                    raise Exception("Invalid response from operation")
                data = result.get("data", None)
                message = result.get("message", None)
                return self.generate_response(data, message)
            except IntegrityError as e:
                await session.rollback()
                message = await self.get_pymysql_message(e)
                return self.generate_error_response(message)
            except Exception as e:
                await session.rollback()
                raise e
                # return self.generate_error_response(f"An unexpected error occurred: {e}")

    async def get_pymysql_message(self, e):
        if not isinstance(e.orig, pymysql.MySQLError):
            return str(e)
        ERROR_CODE = e.orig.args[0]
        COLUMN = None
        VALUE = None
        message = str(e.orig)

        print(ERROR_CODE)

        if "for key" in message:
            message = message.replace('\")', '').replace('\"', '')
            VALUE = message.split('Duplicate entry')[1].split(
                'for key')[0].strip()
            COLUMN = message.split('for key')[1].split(' ')[1].strip()
            COLUMN = COLUMN.strip("'")
            COLUMN = ' '.join(word.capitalize() for word in COLUMN.split('_'))
            COLUMN = f"'{COLUMN}'"

        if ERROR_CODE == 1062:
            message = f"Duplicate value {VALUE} for {COLUMN}. Please try again with a different value."
        if ERROR_CODE == 1451:
            message = (
                "Failed to delete/update because one or more selected items are linked to other records. "
                "Please verify that none of the selected items are linked to other records."
            )
        return message

    def generate_response(self, data, message):
        # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOG - Message: {message}")
        return {"success": True, "data": data, "message": message}

    def generate_error_response(self, message):
        # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LOG - Error: {message}")
        return {
            "success": False,
            "data": None,
            "error": message,
            "message": message
        }
