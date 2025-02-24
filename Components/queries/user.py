import uuid
from sqlalchemy import func, select, update
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from Components.queries.base_query import BaseQuery
from ..tables.models import Role, User

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
                user.pop("id", None)
                user.pop("color", None)
                user.pop("role_name", None)
                user["id"] = str(uuid.uuid4())

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
            # query = select(User)
            user = aliased(User)
            role = aliased(Role)
            query = select(
                user.id,
                user.profile_pic,
                (user.first_name + " " + user.last_name).label("full_name"),
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
                # remove unecessary fields
                user.pop("color", None)
                user.pop("role_name", None)
                user.pop("profile_pic_blob", None)
                user.pop("created_at", None)
                                
                profile_pic_buffer = user.pop("profile_pic_buffer", None)
                if profile_pic_buffer:
                    profile_pic = await self.image_helper.convert_to_image(profile_pic_buffer)
                    profile_pic_name = await self.image_helper.save_image(profile_pic, user["id"], self.user_photos_path )
                    user["profile_pic"] = profile_pic_name
                
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


    def generate_user_message(self, user_count, query_type):
        return f"{user_count} User{'' if user_count == 1 else 's'} {query_type} successfully"
    
