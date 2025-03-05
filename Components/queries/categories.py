import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.queries.base_query import BaseQuery
from ..tables.models import Category

class CategoryQueries(BaseQuery):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)
    
    # ? Insert
    async def insert_categories(self, categories: list):
        async def operation(session):
            for category in categories:
                # removing unnecessary fields
                category.pop("id", None)
                category_id = str(uuid.uuid4())
                category["id"] = category_id

                b = Category(**category)
                session.add(b)
            return {"message": self.generate_category_message(len(categories), "added"), "data": None}
        return await self.execute_query(operation)
    
    # ? Select

    async def get_categories(self):
        async def operation(session):
            result = await session.execute(select(Category))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"message": self.generate_category_message(len(data), "fetched"), "data": data}
        return await self.execute_query(operation)
    
    async def fetch_via_id(self, id_list: list):
        async def operation(session):
            result = await session.execute(select(Category).where(Category.id.in_(id_list)))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"message": self.generate_category_message(len(data), "fetched"), "data": data}
        return await self.execute_query(operation)
    
    async def paged_categories(self, data: dict):
        async def operation(session):
            query = select(Category)
            result = await self.query_helper.get_paged_data(session, Category,  data, query)
            return {"data": {"items": result["data"], "total_count": result["total_count"]}, "message": "Categories fetched successfully"}
        return await self.execute_query(operation)
    
    # ? Update

    async def update_categories(self, categories: list):
        async def operation(session):
            for category in categories:
                stmt = (
                    update(Category)
                    .where(Category.id == category["id"])
                    .values(**{key: value for key, value in category.items() if key != "id"})
                )
                await session.execute(stmt)
            return {"message": self.generate_category_message(len(categories), "updated"), "data": None}
        return await self.execute_query(operation)
    
    # ? Delete

    async def delete_categories(self, categories: list):
        async def operation(session):
            result = await session.execute(Category.__table__.delete().where(Category.id.in_(categories)))
            return {"message": self.generate_category_message(result.rowcount, "deleted"), "data": None}
        return await self.execute_query(operation)
            

    def generate_category_message(self, count, action):
        return f"{count} Categor{'y' if count == 1 else 'ies'} {action} successfully"    
