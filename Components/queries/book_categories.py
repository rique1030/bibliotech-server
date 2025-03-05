from sqlalchemy import func, select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.queries.base_query import BaseQuery
# from Components.queries.book_borrow import BorrowedBookQueries
from ..tables.models import BookCategory, Category

class BookCategoryQueries(BaseQuery):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    async def insert_book_categories(self, book_categories: list):
        async def operation(session):
            for book_category in book_categories:
                b = BookCategory(**book_category)
                session.add(b)
            return {"message": self.generate_book_category_message(len(book_categories), "added"), "data": None}
        return await self.execute_query(operation)
        
    async def fetch_via_book_id(self, book_id: list):
        async def operation(session):
            result = await session.execute(select(BookCategory).where(BookCategory.book_id.in_(book_id)))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"data": data , "message": self.generate_book_category_message(len(data), "fetched")}
        return await self.execute_query(operation)
        
    async def paged_count(self, data: dict):
        async def operation(session):
            category = aliased(Category)
            bookCategory = aliased(BookCategory) #C
            query = select(
                category.name,
                category.description,
                func.count(bookCategory.category_id).label("book_count")
            ).join(category, bookCategory.category_id == category.id).group_by(category.name, category.description)
            result = await self.query_helper.get_paged_data(session, BookCategory, data, query)
            return {"data": {"items": result["data"],"total_count": result["total_count"]}, "message": "Books fetched successfully"}    
        return await self.execute_query(operation)

    async def paged_book_categories(self, data: dict):
        async def operation(session):
            bookCategory = aliased(BookCategory)
            category = aliased(Category)
            query = select(
                category.name,
                category.description,
                func.count(bookCategory.category_id).label("book_count")
            ).join(category, bookCategory.category_id == category.id).group_by(category.name, category.description)
            result = await self.query_helper.get_paged_data(session, [bookCategory, category], data, query)
            return {"data": {"items": result["data"], "total_count": result["total_count"]}, "message": "Books fetched successfully"}
        return await self.execute_query(operation)

    async def delete_book_categories(self, book_ids: list):
        async def operation(session):
            result = await session.execute(BookCategory.__table__.delete().where(BookCategory.book_id.in_(book_ids)))
            return {"message": self.generate_book_category_message(result.rowcount, "deleted"), "data": None}
        return await self.execute_query(operation)
    
    def generate_book_category_message(self, count: int, action: str) -> str:
        return f"{count} Book Categor{'y' if count == 1 else 'ies'} {action} successfully"
    