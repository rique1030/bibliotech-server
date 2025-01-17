from sqlalchemy.orm import Session
from .query_helper import QueryHelper
from ..tables.models import Category

class CategoryQueries:
    def __init__(self, session: Session):
        self.session = session
        self.query_helper = QueryHelper(session)
    
    """
    Insert
    --------------------------------------------------
    """
    
    def insert_multiple_categories(self, categories: list):
        """
        Inserts multiple categories into the database.
        """
        try:
            self.session.bulk_insert_mappings(Category, categories)
            self.session.commit()
            # Return the number of categories inserted
            return len(categories)
        except Exception as e:
            self.session.rollback()
            raise e
    
    """
    Select
    --------------------------------------------------
    """

    def get_all_categories(self):
        """
        Returns all categories from the database.
        """
        try:
            return self.session.query(Category).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_paged_categories(
        self,
        page: int = 0,
        per_page: int = 15,
        filters: dict = None,
        order_by: str = "id",
        order_direction: str = "asc"
    ) -> list:
        """
        Returns a list of categories in the database, sorted and filtered according
        to the input parameters.
        """
        try:
            return self.query_helper.get_paged_data(
                Category, page, per_page, filters, order_by, order_direction
            )
        except Exception as e:
            self.session.rollback()
            raise e

    def get_categories_by_id(self, category_ids: list) -> list:
        """
        Returns a list of categories with the given IDs from the database.
        """
        try:
            result = self.session.query(Category).filter(Category.id.in_(category_ids)).all()
            if result is None:
                return []
            return self.query_helper.model_to_dict(result)
        except Exception as e:
            self.session.rollback()
            raise e
    
    """
    Update
    --------------------------------------------------
    """

    def update_categories(self, categories: list):
        """
        Updates the categories in the database.
        """
        try:
            self.session.bulk_update_mappings(Category, categories)
            # TODO: add commit
            self.session.commit()
            # Return the number of categories updated
            return len(categories)
        except Exception as e:
            self.session.rollback()
            raise e
    
    """
    Delete
    --------------------------------------------------
    """

    def delete_categories_by_id(self, category_ids: list):
        """
        Deletes the categories with the given IDs from the database.
        """
        try:
            self.session.query(Category).filter(Category.id.in_(category_ids)).delete()
            self.session.commit()

            # Return the number of categories deleted
            return len(category_ids)
        except Exception as e:
            self.session.rollback()
            raise e

