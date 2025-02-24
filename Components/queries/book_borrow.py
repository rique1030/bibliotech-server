# from sqlalchemy import Date, func
# from sqlalchemy.orm import Session, aliased
# from .query_helper import QueryHelper
from datetime import timedelta, datetime
from sqlalchemy import select, update
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.queries.base_query import BaseQuery
from ..tables.models import BorrowedBook, Copy, User, Catalog

class BorrowedBookQueries(BaseQuery):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)
        
    # ? Insert

    async def insert_borrow(self, book: dict, user: dict, span: int = 1):
        async def operation(session):
            b = await session.execute(select(BorrowedBook).where(BorrowedBook.copy_id == book.get("id"), BorrowedBook.user_id == user.get("id")))
            borrowed_book = b.scalar_one_or_none()
            if borrowed_book:
                return {"message": "Book is already borrowed by user", "data": None}
            entry = {
                "copy_id": book.get("id"),
                "user_id": user.get("id"),
                "borrowed_date": datetime.now(),
                "due_date": datetime.now() + timedelta(days=span)
                }
            b = BorrowedBook(**entry)
            session.add(b)
            """ Update copy status to borrowed """
            stmt = (
                update(Copy).where(Copy.id == book.get("id")).values(status="borrowed")
            )
            await session.execute(stmt)
            return {"message": "Book borrowed successfully", "data": None}
        return await self.execute_query(operation)
    
    # ? Delete

    async def delete_borrow(self, book: dict, user: dict):
        async def operation(session):
            b = await session.execute(select(BorrowedBook).where(BorrowedBook.copy_id == book.get("id"), BorrowedBook.user_id == user.get("id")))
            borrowed_book = b.scalar_one_or_none()
            if not borrowed_book:
                return {"message": "Book is not borrowed by user", "data": None}
            await session.delete(borrowed_book)
            """ Update copy status to available """
            stmt = (
                update(Copy).where(Copy.id == book.get("id")).values(status="available")
            )
            await session.execute(stmt)
            return {"message": "Book returned successfully", "data": None}
        return await self.execute_query(operation)

    async def paged_borrowings(self, data: dict):
        async def operation(session):
            copy = aliased(Copy)
            catalog = aliased(Catalog)
            user = aliased(User)
            query = select(
                copy.id,
                (user.first_name + " " + user.last_name).label("full_name"),
                copy.access_number,
                catalog.title,
                catalog.author,
                copy.status,
                BorrowedBook.borrowed_date,
                BorrowedBook.due_date,
            ).join(copy, BorrowedBook.copy_id == copy.id).join(catalog, copy.catalog_id == catalog.id).join(user, BorrowedBook.user_id == user.id)
            result = await self.query_helper.get_paged_data(session, [BorrowedBook, copy, catalog, user], data, query)
            return {"data": {"items": result["data"], "total_count": result["total_count"]}, "message": "Borrowings fetched successfully"}
        return await self.execute_query(operation)

        