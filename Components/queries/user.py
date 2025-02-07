from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .query_helper import QueryHelper
from ..tables.models import User

class UserQueries:
    def __init__(self, session: Session):
        self.session_factory = session
        self.query_helper = QueryHelper(session)
        # self.populate_user()
        
    """
    Insert
    --------------------------------------------------
    """

    async def insert_multiple_users(self, users: list):
        """
        Inserts multiple users into the database.
        """
        async with self.session_factory() as session:
            try:
                result = await session.execute(User.__table__.insert(), users)
                await session.commit()
                
                return {"success": True, "message": f"{result.rowcount} User{'' if result.rowcount == 1 else 's'} added successfully"}
            except IntegrityError as e:
                await session.rollback()
                return {"success": False, "error": "One of the submitted users already exists with the same email."}
            except Exception as e:
                await session.rollback()
                return {"success": False, "error": f"An unexpected error occurred"}
    
    """
    Select
    --------------------------------------------------
    """

    async def get_paged_users(
        self,
        page: int = 0,
        per_page: int = 15,
        filters: dict = None,
        order_by: str = "id",
        order_direction: str = "asc"
    ) -> list:
        """
        Returns a list of users in the database, sorted and filtered according
        to the input parameters.
        """
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(User).order_by(
                        getattr(User, order_by).asc() if order_direction == "asc" else getattr(User, order_by).desc()
                    ).limit(per_page).offset(page * per_page)
                )
                return [dict(row) for row in result]
            except Exception as e:
                await session.rollback()
                raise e

    async def get_paged_user_records(
            self,
            page: int = 0,
            per_page: int = 15,
            filters: dict = None,
            order_by: str = "id",
            order_direction: str = "asc"
    ) -> list:
        """
        Returns a list of users in the database, sorted and filtered according
        to the input parameters.
        """
        try:
            # return await self.query_helper.get_paged_data(User, page, per_page, filters, order_by, order_direction)
            query = (
                await self.session.execute(
                    select(User).order_by(
                        getattr(User, order_by).asc() if order_direction == "asc" else getattr(User, order_by).desc()
                    ).limit(per_page).offset(page * per_page)
                )
            )
            pass

        except Exception as e:
            await self.session.rollback()
            raise e

    

    async def get_users_by_id(self, user_ids: list) -> list:
        """
        Returns a list of users with the given IDs from the database.
        """
        async with self.session_factory() as session:
            try:
                result = await session.execute(select(User).where(User.id.in_(user_ids)))
                return [dict(row) for row in result]
            except Exception as e:
                await session.rollback()
                raise e
    
    async def get_user_by_email_and_password(self, email: str, password: str) -> User:
        """
        Returns the user with the given email and password in the database.
        """
        async with self.session_factory() as session:
            try:
                result = await session.execute(select(User).where(User.email == email, User.password == password))
                row = result.first()
                if row is None:
                    return None
                return row.User.to_dict()
            except Exception as e:
                await session.rollback()
                raise e
    
    """
    Update
    --------------------------------------------------
    """

    async def update_users(self, user: list):
        """
        Updates the users in the database.
        """
        async with self.session_factory() as session:
            try:
                result = await session.execute(User.__table__.update().values(user).where(User.id == user["id"]))
                await session.commit()

                # Return the number of users updated
                return {"success": True, "message": f"{result.rowcount} User{'' if result.rowcount == 1 else 's'} edited successfully"}
            except IntegrityError as e:
                await session.rollback()
                return {"success": False, "error": "One of the submitted users already exists with the same email."}
            except Exception as e:
                await session.rollback()
                print(e)
                return {"success": False, "error": f"An unexpected error occurred"}
    
    """
    Delete
    --------------------------------------------------
    """

    async def delete_users_by_id(self, user_ids: list):
        """
        Deletes the users with the given IDs from the database.
        """
        async with self.session_factory() as session:
            try:
                result = await session.execute(User.__table__.delete().where(User.id.in_(user_ids)))
                await session.commit()

                # Return the number of users deleted
                return {"success": True, "message": f"{result.rowcount} User{'' if result.rowcount == 1 else 's'} deleted successfully"}
            except Exception as e:
                await session.rollback()
                return {"success": False, "error": f"An unexpected error occurred"}

    async def populate_user(self):
        async with self.session_factory() as session:
            try: 
                user_count = await session.execute(select(func.count(User.id )))
                count = user_count.scalar()
                if count == 0:
                    users = [
                        {   
                            "id": 0,
                            "profile_pic": "default",
                            "first_name": "admin",
                            "last_name": "admin",
                            "email": "admin@admin.com",
                            "password": "admin", 
                            "school_id": "4DM1N",
                            "role_id": 1,
                            "is_verified": True,
                            "created_at": None,
                        }]
                    await self.insert_multiple_users(users)
            except Exception as e:
                await session.rollback()
                raise Exception(f"Error populating users: {e}")

