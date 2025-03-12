import uuid
from sqlalchemy import func, select, update
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.queries.base_query import BaseQuery
from ..tables.models import BorrowedBook, Copy, Role, User, Catalog

users = [
    {   
        "id": "4DM1N",
        "profile_pic": "default",
        "first_name": "admin",
        "last_name": "admin",
        "email": "admin@admin.com",
        "password": "admin", 
        "school_id": "4DM1N",
        "role_id": "ADMIN",
        "is_verified": True,
        "created_at": None,
    }
]

class UserQueries(BaseQuery):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)
    # ? Insert

    async def insert_users(self, users: list):
        async def operation(session):
            for user in users:
                # removing unnecessary fields
                if not user.get("id") == "4DM1N":
                    user.pop("id", None)
                    user["id"] = str(uuid.uuid4())
                user.pop("color", None)
                user.pop("role_name", None)

                # saving profile pic
                profile_pic_buffer = user.pop("profile_pic_buffer", None)
                if profile_pic_buffer:
                    profile_pic = await self.image_helper.convert_to_image(profile_pic_buffer)
                    profile_pic_name = await self.image_helper.save_image(profile_pic, user["id"], self.user_photos_path)
                    user["profile_pic"] = profile_pic_name
                else:
                    user["profile_pic"] = "default"


                b = User(**user)
                session.add(b)
            return {"message": self.generate_user_message(len(users), "added"), "data": None}  
        return await self.execute_query(operation)
    
    # ? select
    async def paged_users(self, payload: dict):
        async def operation(session):
            user = aliased(User)
            role = aliased(Role)
            query = select(
                user.id,
                user.profile_pic,
                user.first_name,
                user.last_name,
                user.email,
                user.password,
                user.school_id,
                role.role_name,
                role.color,
                user.is_verified,
                user.created_at
            ).join(role, user.role_id == role.id)
            result = await self.query_helper.get_paged_data(session, [user, role], payload, query)
            return {"data": {"items": result["data"], "total_count": result["total_count"]}, "message": "Users fetched successfully"}
        return await self.execute_query(operation)

    async def fetch_via_id(self, ids: list):
        async def operation(session):
            result = await session.execute(select(User).where(User.id.in_(ids)))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            
            return {"data": data , "message": "User fetched successfully"}
        return await self.execute_query(operation)
    
    async def fetch_via_email_and_password(self, email: str, password: str):
        async def operation(session):
            result = await session.execute(select(User).where(User.email == email, User.password == password))
            data = result.scalars().all()
            data = await self.query_helper.model_to_dict(data)
            return {"data": data , "message": "User fetched successfully"}
        return await self.execute_query(operation)
    
    # ? Update

    async def update_users(self, users: dict):
        async def operation(session):
            for user in users:
                # fetch existing data
                existing_user = await session.execute(select(User).where(User.id == user["id"]))
                existing_user = existing_user.scalar_one_or_none()
                if not existing_user:
                    continue

                # remove unecessary fields
                user.pop("color", None)
                user.pop("role_name", None)
                user.pop("profile_pic_blob", None)
                user.pop("created_at", None)
                user.pop("name_updated", None)
                user.pop("password_updated", None)
                user.pop("email_updated", None)

                if "password" in user and user["password"] != existing_user.password:
                    user["password_updated"] = func.now()
                if ("first_name" in user and user["first_name"] != existing_user.first_name) or \
                    ("last_name" in user and user["last_name"] != existing_user.last_name):
                    user["name_updated"] = func.now()
                if "email" in user and user["email"] != existing_user.email:
                    user["email_updated"] = func.now()

                # save profile pic
                profile_pic_buffer = user.pop("profile_pic_buffer", None)
                if profile_pic_buffer:
                    profile_pic = await self.image_helper.convert_to_image(profile_pic_buffer)
                    profile_pic_name = await self.image_helper.save_image(profile_pic, user["id"], self.user_photos_path )
                    user["profile_pic"] = profile_pic_name

                # update user
                stmt = (
                    update(User)
                    .where(User.id == user["id"])
                    .values(**{key: value for key, value in user.items() if key != "id"})
                )
                await session.execute(stmt)
            return {"message": self.generate_user_message(len(users), "updated"), "data": None}
        return await self.execute_query(operation)

    # ? Delete

    async def delete_users(self, user_ids: list):
        async def operation(session):
            result = await session.execute(User.__table__.delete().where(User.id.in_(user_ids)))
            await session.commit()
            return {"message": self.generate_user_message(result.rowcount, "deleted"), "data": None}
        return await self.execute_query(operation)

    async def populate_users(self):
        async def operation(session):
            print("Populating users...")
            user_count = await session.execute(select(func.count(User.id)))
            count = user_count.scalar()
            if count == 0:
                await self.insert_users(users)
                return {"data": None, "message": "Users populated successfully"}
            return {"data": None, "message": "Users already populated"}
        return await self.execute_query(operation)

    async def get_borrowed_books(self, user_id: str):
        async def operation(session):
            catalog = aliased(Catalog)
            copy = aliased(Copy)
            borrow = aliased(BorrowedBook)
            result = await session.execute(select(
                borrow.id, 
                borrow.copy_id,
                copy.access_number,
                copy.status,
                copy.catalog_id,
                catalog.call_number,
                catalog.title,
                catalog.author,
                catalog.publisher,
                catalog.cover_image,
                catalog.description
            )
                .join(copy, borrow.copy_id == copy.id)
                .join(catalog, copy.catalog_id == catalog.id)
                .where(borrow.user_id == user_id))
            result = [dict(row) for row in result.mappings()]
            return {"data": result , "message": "User fetched successfully"}
        return await self.execute_query(operation)

    async def count_all_users(self):
        async def operation(session):
            user_count = await session.execute(select(func.count(User.id)))
            count = user_count.scalar()
            return {"data": count, "message": "User count fetched successfully"}
        return await self.execute_query(operation)

    async def count_user_roles(self):
        async def operation(session):
            role = aliased(Role)
            user = aliased(User)
            role_count = await session.execute(select(
                role.role_name,
                role.color,
                func.count(user.id).label("count")
            ).join(user, role.id == user.role_id).group_by(role.role_name, role.color))
            count = [{"label": row[0], "color": row[1], "value": row[2]} for row in role_count]
            return {"data": count, "message": "User count by role fetched successfully"}
        return await self.execute_query(operation)

    def generate_user_message(self, user_count, query_type):
        return f"{user_count} User{'' if user_count == 1 else 's'} {query_type} successfully"
    
