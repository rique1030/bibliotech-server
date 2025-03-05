from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from Components.queries.base_query import BaseQuery

class BookCopy(BaseQuery):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)
    
    async def fetch_books_by_access_number(self, access_numbers: list):
        async def operation(session):
            result = await session.query(Book).filter(Book.access_number.in_(access_numbers)).all()
        pass

    async def fetch_paged_book_copies(self, page, per_page, filters, order_by, order_direction):
        pass
    
    async def count_book_copies_by_book_catalog(self, book_id):
        pass

    async def fetch_book_copies_by_book_id(self, book_id):
        pass

