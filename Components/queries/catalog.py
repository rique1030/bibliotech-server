import uuid
from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.managers.book_categories import BookCategoryManager
from Components.managers.categories import CategoryManager
from Components.queries.base_query import BaseQuery
from ..tables.models import BookCategory, Catalog

class CatalogQueries(BaseQuery):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], book_category_manager: BookCategoryManager, category_manager: CategoryManager):        
        super().__init__(session_factory)
        self.book_category_queries = book_category_manager.book_category_queries
        self.category_queries = category_manager.category_queries
    
    
    async def insert_catalogs(self, books: list):
        async def operation(session):
            catalog = []
            book_categories = []
            for book in books:
                # removing unnecessary fields
                book.pop("id", None)
                book_id = str(uuid.uuid4())
                book["id"] = book_id

                # saving cover image
                cover_image_buffer = book.pop("cover_image_buffer", None)
                if cover_image_buffer:
                    cover_image = await self.image_helper.convert_to_image(cover_image_buffer)
                    cover_name = await self.image_helper.save_image(cover_image, book_id, self.book_cover_path)
                    book["cover_image"] = cover_name
                else:
                    book["cover_image"] = "default"

                # saving book categories
                categories = book.pop("book_categories", [])
                for category in categories:
                    book_categories.append(
                        BookCategory(
                            id=str(uuid.uuid4()),
                            book_id=book_id,
                            category_id=category.get("id")
                        )
                    )
                # saving book
                catalog.append(Catalog(**book))

            session.add_all(catalog)
            session.add_all(book_categories)
                # await self.book_category_queries.insert_book_categories(book_categories)
            return {"message": self.generate_book_message(len(books), "added"), "data": None}
        return await self.execute_query(operation)
    
    async def fetch_via_ids(self, book_ids: list):
        async def operation(session):
            result = await session.execute(select(Catalog).where(Catalog.id.in_(book_ids)))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            for book in data:
                book_categories = await self.book_category_queries.fetch_via_book_id([book["id"]])
                if len(book_categories["data"]) == 0:
                    continue
                categories = await self.category_queries.fetch_via_id([ cat["category_id"] for cat in book_categories["data"]  ])
                book["book_category_ids"] = [category["id"] for category in categories["data"]]
                book["old_ids"] = [category["id"] for category in book_categories["data"]]
            return {"data": data, "message": "Books fetched successfully"}
        return await self.execute_query(operation)

    async def paged_catalogs(self, data: dict):
        async def operation(session):
            query = select(Catalog)
            result = await self.query_helper.get_paged_data(session, Catalog,  data, query)
            for book in result["data"]:
                book_categories = await self.book_category_queries.fetch_via_book_id([book["id"]])
                if len(book_categories["data"]) == 0:
                    continue
                categories = await self.category_queries.fetch_via_id([ cat["category_id"] for cat in book_categories["data"]  ])
                book["book_categories"] = categories["data"]
            return {"data": {"items": result["data"], "total_count": result["total_count"]}, "message": "Books fetched successfully"}
        return await self.execute_query(operation)

    async def update_catalogs(self, books: list):
        async def operation(session):
            for book in books:

                # removing unnecessary fields
                book.pop("cover_image_blob", None)
                new_ids = book.pop("new_ids", [])
                
                old_ids = book.pop("old_ids", [])
                book.pop("book_categories", [])
                book.pop("book_category_ids", [])

                cover_image_buffer = book.pop("cover_image_buffer", None)
                if cover_image_buffer:
                    cover_image = await self.image_helper.convert_to_image(cover_image_buffer)
                    cover_name = await self.image_helper.save_image(cover_image, book["id"], self.book_cover_path)
                    book["cover_image"] = cover_name

                stmt = (
                    update(Catalog)
                    .where(Catalog.id == book["id"])
                    .values(**{key: value for key, value in book.items() if key != "id"})
                )
                await session.execute(stmt) 

                new_ids = set(new_ids)
                old_ids = set(old_ids)

                ids_to_add = new_ids - old_ids
                ids_to_remove = old_ids - new_ids
                
                cat_to_add = [BookCategory(book_id=book["id"], category_id=id) for id in ids_to_add]

                session.add_all(cat_to_add)
                await session.flush()
                stmt = (delete(BookCategory).where(BookCategory.id.in_(ids_to_remove)))

                await session.execute(stmt)


            return {"message": self.generate_book_message(len(books), "updated"), "data": None}
        return await self.execute_query(operation)

    async def delete_catalogs(self, book_ids: list):
        async def operation(session):
            result = await session.execute(
                Catalog.__table__.delete().where(Catalog.id.in_(book_ids))
            )
            return {"message": self.generate_book_message(result.rowcount, "deleted"), "data": None}
        return await self.execute_query(operation)


    def generate_book_message(self, book_count, query_type):
        return f"{book_count} Book{'' if book_count == 1 else 's'} {query_type} successfully"
    
