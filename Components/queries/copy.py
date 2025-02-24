from sqlalchemy import func, select, update
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.QRManager import QRManager
from Components.queries.base_query import BaseQuery
from Components.tables.models import Catalog, BookCategory, Copy, Category

class CopyQueries(BaseQuery):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)
        self.qr = QRManager()

    # ? ====================[ INSERT ]=====================================================================================

    async def insert_copies(self, books: list):
        async def operation(session):
            for book in books:
                b = Copy(**book)
                session.add(b)
            return {"message": self.generate_book_message(len(books), "added"), "data": None}
        return await self.execute_query(operation)

    # ? ====================[ UPDATE ]=====================================================================================

    async def update_copies(self, books: list):
        async def operation(session):
            for book in books:
                stmt = (
                    update(Copy)
                    .where(Copy.id == book["id"])
                    .values(**{key: value for key, value in book.items() if key != "id"})
                )
                await session.execute(stmt)
            return {"message": self.generate_book_message(len(books), "updated"), "data": None}
        return await self.execute_query(operation)


    # ? ====================[ SELECT ]=====================================================================================    

    async def paged_copies(self, data: dict):
        async def operation(session):
            instance = aliased(Copy)
            catalog = aliased(Catalog)
            query = select(
                    instance.id,
                    instance.access_number,
                    instance.status,
                    instance.catalog_id,
                    catalog.call_number,
                    catalog.title,
                    catalog.author,
                    catalog.publisher,
                    catalog.cover_image,
                    catalog.description,
                    ).join(catalog, instance.catalog_id == catalog.id)
            result = await self.query_helper.get_paged_data(session, instance, data, query)
            return {"data": {"items": result["data"], "total_count": result["total_count"]}, "message": "Books fetched successfully"}
        return await self.execute_query(operation)
    
    async def paged_count(self, data: dict):
        async def operation(session):
            instance = aliased(Copy)
            catalog = aliased(Catalog)
            query = select(
                catalog.id,
                catalog.call_number,
                catalog.title,
                catalog.author,
                catalog.publisher,
                catalog.cover_image,
                catalog.description,
                func.count(instance.id).label("copies"),
            ).join(catalog, instance.catalog_id == catalog.id).group_by(catalog.id)
            result = await self.query_helper.get_paged_data(session, [instance, catalog], data, query)        
            return {"data": {"items": result["data"], "total_count": result["total_count"]}, "message": "Books fetched successfully"}
        return await self.execute_query(operation)

    async def fetch_via_id(self, ids: list):
        async def operation(session):
            instance = aliased(Copy)
            catalog = aliased(Catalog)
            result = await session.execute(
                select(
                    instance.id,
                    instance.access_number,
                    instance.status,
                    instance.catalog_id,
                    catalog.call_number,
                    catalog.title,
                    catalog.author,
                    catalog.publisher,
                    catalog.cover_image,
                    catalog.description,
                    ).join(catalog, instance.catalog_id == catalog.id)
                .where(instance.id.in_(ids))
            )
            result = [dict(row) for row in result.mappings()]
            return {
                "data": result,
                "message": self.generate_book_message(len(result), "fetched"),
            }
        return await self.execute_query(operation)
    

    async def fetch_via_access_number(self, access_numbers: list):
        async def operation(session):
            instance = aliased(Copy)
            catalog = aliased(Catalog)
            result = await session.execute(
                select(
                    instance.id,
                    instance.access_number,
                    instance.status,
                    instance.catalog_id,
                    catalog.call_number,
                    catalog.title,
                    catalog.author,
                    catalog.publisher,
                    catalog.cover_image,
                    catalog.description,
                    ).join(catalog, instance.catalog_id == catalog.id)
                .where(instance.access_number.in_(access_numbers))
            )
            result = [dict(row) for row in result.mappings()]
            return {
                "data": result,
                "message": self.generate_book_message(len(result), "fetched"),
            }
        return await self.execute_query(operation)
    

    # ? delete

    async def delete_copies(self, book_ids: list):
        async def operation(session):
            result = await session.execute(
                Copy.__table__.delete().where(Copy.id.in_(book_ids))
            )
            return {"message": self.generate_book_message(result.rowcount, "deleted"), "data": None}
        return await self.execute_query(operation)


    def generate_book_message(self, book_count, query_type):
        return f"{book_count} Book Cop{'y' if book_count == 1 else 'ies'} {query_type} successfully"
    
