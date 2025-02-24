import asyncio
import uuid
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.queries.base_query import BaseQuery
from ..tables.models import Role


roles = [
    {
        "id": "ADMIN",
        "role_name": "Admin", 
        "account_view": True, 
        "account_insert": True, 
        "account_update": True, 
        "account_delete": True, 
        "roles_view": True, 
        "roles_insert": True, 
        "roles_update": True, 
        "roles_delete": True, 
        "books_view": True, 
        "books_insert": True, 
        "books_update": True, 
        "books_delete": True, 
        "categories_view": True, 
        "categories_insert": True, 
        "categories_update": True, 
        "categories_delete": True, 
        "notes": "Default admin role",
        "color": "#4caf50"
    },
    {
        "id": "U5ER",
        "role_name": "User", 
        "account_view": False, 
        "account_insert": False, 
        "account_update": False, 
        "account_delete": False, 
        "roles_view": False, 
        "roles_insert": False, 
        "roles_update": False, 
        "roles_delete": False, 
        "books_view": False, 
        "books_insert": False, 
        "books_update": False, 
        "books_delete": False, 
        "categories_view": False, 
        "categories_insert": False, 
        "categories_update": False, 
        "categories_delete": False, 
        "notes": "Default user role",
        "color": "#5b40e4"
    },
]

class RoleQueries(BaseQuery):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)
        self.roles = roles
    # ? insert 

    async def insert_roles(self, roles: list):
        async def operation(session):
            for role in roles:
                role["id"] = str(uuid.uuid4())
                b = Role(**role)
                session.add(b)
            return {"message": self.generate_role_message(len(roles), "added"), "data": None}
        return await self.execute_query(operation)

    # ? select
    async def get_roles(self):
        async def operation(session):
            result = await session.execute(select(Role))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"data": data , "message": "Roles fetched successfully"}
        return await self.execute_query(operation)
            
    async def paged_roles(self, data: dict):
        async def operation(session):
            query = select(Role)
            result = await self.query_helper.get_paged_data(session, Role,  data, query)
            return {"data": {"items": result["data"], "total_count": result["total_count"]}, "message": "Roles fetched successfully"}
        return await self.execute_query(operation)
    
    async def fetch_via_id(self, id_list: list):
        async def operation(session):
            result = await session.execute(select(Role).where(Role.id.in_(id_list)))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"data": data , "message": "Role fetched successfully"}
        return await self.execute_query(operation)
    
    # ? update
    async def update_roles(self, roles: list):
        async def operation(session):
            for role in roles:
                stmt = (
                    update(Role)
                    .where(Role.id == role["id"])
                    .values(**{key: value for key, value in role.items() if key != "id"})
                )
                await session.execute(stmt)
            return {"message": self.generate_role_message(len(roles), "updated"), "data": None}
        return await self.execute_query(operation)
    
    # ? delete
    
    async def delete_roles(self, role_ids: list):
        async def operation(session):
            result = await session.execute(
                Role.__table__.delete().where(Role.id.in_(role_ids))
            )
            return {"message": self.generate_role_message(result.rowcount, "deleted"), "data": None}
        return await self.execute_query(operation)


    async def populate_roles(self):
        async def operation(session):
            roles_count = await session.execute(select(func.count(Role.id)))
            count = roles_count.scalar()
            if count == 0:
                print("Populating roles...")
                await self.insert_roles(self.roles)
                return {"data": None, "message": "Roles populated successfully"}
            return {"data": None, "message": "Roles already populated"}
        return await self.execute_query(operation)


    def generate_role_message(self, role_count, query_type):
        return f"{role_count} Role{'' if role_count == 1 else 's'} {query_type} successfully"
    

    # """
    # Delete
    # --------------------------------------------------
    # """
    # async def delete_roles_by_id(self, role_ids: list):
    #     """
    #     Deletes the roles with the given IDs from the database.
    #     """
    #     async with self.session_factory() as session:
    #         try:
    #             await session.query(Role).filter(Role.id.in_(role_ids)).delete()
    #             await session.commit()
    #             return {"success": True, "message": f"{len(role_ids)} Role{'' if len(role_ids) == 1 else 's'} deleted successfully"}
    #         except IntegrityError as e:
    #             await session.rollback()
    #             return {"success": False, "error": "The role cannot be deleted because it is currently in use. Please remove it from all accounts before deleting."}
    #         except Exception as e:
    #             await session.rollback()
    #             return {"success": False, "error": f"An unexpected error occurred"}
    
    #     async with self.session_factory() as session:
    #         try:
    #             roles_count = await session.execute(select(func.count(Role.id)))
    #             count = roles_count.scalar()
    #             if count == 0:
    #                 await self.insert_multiple_roles(roles)
    #         except Exception as e:
    #             await session.rollback()
    #             raise Exception(f"Error populating roles: {e}")
