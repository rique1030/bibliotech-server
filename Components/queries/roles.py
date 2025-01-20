from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .query_helper import QueryHelper
from ..tables.models import Role

class RoleQueries:
    def __init__(self, session: Session):
        self.session = session
        self.query_helper = QueryHelper(session)
        self.populate_roles()
    
    """
    Insert
    --------------------------------------------------
    """
    def insert_multiple_roles(self, roles: list):
        """
        Inserts multiple roles into the database.
        """
        try:
            self.session.bulk_insert_mappings(Role, roles)
            self.session.commit()
            return {"success": True, "message": f"{len(roles)} Role{'' if len(roles) == 1 else 's'} added successfully"}
        except IntegrityError as e:
            self.session.rollback()
            return {"success": False, "error": "One of the submitted roles already exists with the same name."}
        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": f"An unexpected error occurred"}

    """
    Select
    --------------------------------------------------
    """
    def get_all_roles(self):
        """
        Returns a list of all roles in the database.
        """
        try:
            result = self.session.query(Role).all()
            if result is None:
                return []
            return self.query_helper.model_to_dict(result)
        except Exception as e:
            raise Exception(f"Error retrieving all roles: {e}")

    def get_paged_roles(
        self,
        page: int = 0,
        per_page: int = 15,
        filters: dict = None,
        order_by: str = "id",
        order_direction: str = "asc"
    ) -> list:
        """
        Returns a list of roles in the database, sorted and filtered according
        to the input parameters.
        """
        try:
            return self.query_helper.get_paged_data(
                Role, page, per_page, filters, order_by, order_direction
            )
        except Exception as e:
            raise Exception(f"Error retrieving paged roles: {e}")

    def get_roles_by_id(self, role_ids: list) -> list:
        """
        Returns a list of roles with the given IDs from the database.
        """
        try:
            result = self.session.query(Role).filter(Role.id.in_(role_ids)).all()
            if result is None:
                return []
            return self.query_helper.model_to_dict(result)
        except Exception as e:
            raise Exception(f"Error retrieving roles by ID: {e}")

    """
    Update
    --------------------------------------------------
    """
    def update_roles(self, roles: list):
        """
        Updates the roles in the database.
        """
        try:
            self.session.bulk_update_mappings(Role, roles)
            self.session.commit()
            return {"success": True, "message": f"{len(roles)} Role{'' if len(roles) == 1 else 's'} edited successfully"}
        except IntegrityError as e:
            self.session.rollback()
            raise Exception("One of the submitted roles already exists with the same name.")
        except Exception as e:
            self.session.rollback()
            print(e)
            return {"success": False, "error": f"An unexpected error occurred"}

    """
    Delete
    --------------------------------------------------
    """
    def delete_roles_by_id(self, role_ids: list):
        """
        Deletes the roles with the given IDs from the database.
        """
        try:
            self.session.query(Role).filter(Role.id.in_(role_ids)).delete()
            self.session.commit()
            return {"success": True, "message": f"{len(role_ids)} Role{'' if len(role_ids) == 1 else 's'} deleted successfully"}
        except IntegrityError as e:
            self.session.rollback()
            return {"success": False, "error": "The role cannot be deleted because it is currently in use. Please remove it from all accounts before deleting."}
        except Exception as e:
            self.session.rollback()
            print(e)
            return {"success": False, "error": f"An unexpected error occurred"}



    def populate_roles(self):
        try:
            count = self.session.query(Role).count()
            if count == 0:
                roles = [
                    {
                        "id": 1,
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
                        "id": 2,
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
                self.insert_multiple_roles(roles)
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error populating roles: {e}")