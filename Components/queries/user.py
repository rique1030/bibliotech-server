from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .query_helper import QueryHelper
from ..tables.models import User

class UserQueries:
    def __init__(self, session: Session):
        self.session = session
        self.query_helper = QueryHelper(session)
        self.populate_user()
        
    """
    Insert
    --------------------------------------------------
    """

    def insert_multiple_users(self, users: list):
        """
        Inserts multiple users into the database.
        """
        try:
            self.session.bulk_insert_mappings(User, users)
            self.session.commit()
            
            return {"success": True, "message": f"{len(users)} User{'' if len(users) == 1 else 's'} added successfully"}
        except IntegrityError as e:
            print(e)
            self.session.rollback()
            return {"success": False, "error": "One of the submitted users already exists with the same email."}
        except Exception as e:
            print(e)
            self.session.rollback()
            return {"success": False, "error": f"An unexpected error occurred"}
    
    """
    Select
    --------------------------------------------------
    """

    def get_paged_users(
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
            return self.query_helper.get_paged_data(User, page, per_page, filters, order_by, order_direction)

        except Exception as e:
            self.session.rollback()
            raise e


    def get_users_by_id(self, user_ids: list) -> list:
        """
        Returns a list of users with the given IDs from the database.
        """
        try:
            result = self.session.query(User).filter(User.id.in_(user_ids)).all()
            if result is None:
                return []
            return self.query_helper.model_to_dict(result)
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_user_by_email_and_password(self, email: str, password: str) -> User:
        """
        Returns the user with the given email and password in the database.
        """
        try:
            result = self.session.query(User).filter_by(email=email, password=password).first()
            if result is None:
                return None
            return self.query_helper.model_to_dict(result)
        except Exception as e:
            self.session.rollback()
            raise e
    
    """
    Update
    --------------------------------------------------
    """

    def update_users(self, user: list):
        """
        Updates the users in the database.
        """
        try:
            self.session.bulk_update_mappings(User, user)
            self.session.commit()

            # Return the number of users updated
            return {"success": True, "message": f"{len(user)} User{'' if len(user) == 1 else 's'} edited successfully"}
        except IntegrityError as e:
            self.session.rollback()
            return {"success": False, "error": "One of the submitted users already exists with the same email."}
        except Exception as e:
            self.session.rollback()
            print(e)
            return {"success": False, "error": f"An unexpected error occurred"}
    
    """
    Delete
    --------------------------------------------------
    """

    def delete_users_by_id(self, user_ids: list):
        """
        Deletes the users with the given IDs from the database.
        """
        try:
            self.session.query(User).filter(User.id.in_(user_ids)).delete()
            self.session.commit()

            # Return the number of users deleted
            return {"success": True, "message": f"{len(user_ids)} User{'' if len(user_ids) == 1 else 's'} deleted successfully"}
        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": f"An unexpected error occurred"}

    def populate_user(self):
        try:
            count = self.session.query(User).count()
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
                        # "is_active": True
                    }]
                self.insert_multiple_users(users)
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error populating users: {e}")