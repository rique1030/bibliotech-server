from sqlalchemy.orm import Session
from .query_helper import QueryHelper
from ..tables.models import BookCategory

class BookCategoryQueries:
    def __init__(self, session: Session):
        self.session = session  
        self.query_helper = QueryHelper(session)
    """
    Insert
    --------------------------------------------------
    """
    
    def insert_multiple_book_categories(self, book_categories: list):
        """
        Inserts multiple book categories into the database.
        """
        try:
            self.session.bulk_insert_mappings(BookCategory, book_categories)
            # TODO: add commit
            # self.session.commit()
            # Return the number of book categories inserted
            # return len(book_categories)
        except Exception as e:
            self.session.rollback()
            raise e
    
    """
    Select
    --------------------------------------------------
    """
    def get_book_categories_by_id(self, book_category_ids: list) -> list:
        """
        Returns a list of book categories with the given IDs from the database.
        """
        try:
            return self.session.query(BookCategory).filter(BookCategory.id.in_(book_category_ids)).all()
        except Exception as e:
            self.session.rollback()
            raise e

    """
    Update
    --------------------------------------------------
    """

    def update_book_categories(self, book_categories: list):
        """
        Updates the book categories in the database.
        """
        try:
            self.session.bulk_update_mappings(BookCategory, book_categories)
            # TODO: add commit
            # self.session.commit()
            # Return the number of book categories updated
            return len(book_categories)
        except Exception as e:
            self.session.rollback()
            raise e
    
    """
    Delete
    --------------------------------------------------
    """

    def delete_book_categories_by_id(self, book_category_ids: list):
        """
        Deletes the book categories with the given IDs from the database.
        """
        try:
            self.session.query(BookCategory).filter(BookCategory.id.in_(book_category_ids)).delete()
            self.session.commit()

            # Return the number of book categories deleted
            return len(book_category_ids)
        except Exception as e:
            self.session.rollback()
            raise e

