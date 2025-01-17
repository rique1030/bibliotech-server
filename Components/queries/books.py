from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .query_helper import QueryHelper
from ..tables.models import Book
from ..QRManager import QRManager

class BookQueries:
    def __init__(self, session: Session):
        self.qr = QRManager()        
        self.session = session
        self.query_helper = QueryHelper(session)
    
    """
    Insert
    --------------------------------------------------
    """
    
    def insert_multiple_books(self, books: list):
        """
        Inserts multiple books into the database.
        """
        try:
            self.session.bulk_insert_mappings(Book, books)
            self.session.commit()
            if not self.qr.generate_qr_code(books):
                raise Exception("Failed to generate QR codes for the books")
            # Return the number of books inserted
            return {"success": True, "message": f"{len(books)} Book{'' if len(books) == 1 else 's'} added successfully"}
        except IntegrityError as e:
            self.session.rollback()
            return {"success": False, "error": "One of the submitted books already exists with the same access number or call number."}
        except Exception as e:
            self.session.rollback()
            print(e)
            return {"success": False, "error": f"An unexpected error occurred"}
    
    """
    Select
    --------------------------------------------------
    """

    def get_paged_books(
        self,
        page: int = 0,
        per_page: int = 15,
        filters: dict = None,
        order_by: str = "id",
        order_direction: str = "asc"
    ) -> list:
        """
        Returns a list of books in the database, sorted and filtered according
        to the input parameters.
        """
        try:
            return self.query_helper.get_paged_data(
                Book, page, per_page, filters, order_by, order_direction
            )
        except Exception as e:
            self.session.rollback()
            raise e
        
    
    def get_books_by_access_number(self, access_numbers: list) -> list:
        """
        Returns a list of books with the given access numbers from the database.
        """
        try:
            result = self.session.query(Book).filter(Book.access_number.in_(access_numbers)).all()
            if result is None:
                return []
            return self.query_helper.model_to_dict(result)
        except Exception as e:
            self.session.rollback()
            raise e
    

    def get_books_by_id(self, book_ids: list) -> list:
        """
        Returns a list of books with the given IDs from the database.
        """
        try:
            result = self.session.query(Book).filter(Book.id.in_(book_ids)).all()
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

    def update_books(self, books: list):
        """
        Updates the books in the database.
        """
        try:
            self.session.bulk_update_mappings(Book, books)
            # TODO: add commit
            self.session.commit()
            if not self.qr.generate_qr_code(books):
                raise Exception("Failed to generate QR codes for the books")
            # Return the number of books inserted
            return {"success": True, "message": f"{len(books)} Book{'' if len(books) == 1 else 's'} edited successfully"}
        except IntegrityError as e:
            self.session.rollback()
            return {"success": False, "error": "One of the submitted books already exists with the same access number or call number."}
        except Exception as e:
            self.session.rollback()
            print(e)
            return {"success": False, "error": f"An unexpected error occurred"}
            # //return e
    
    """
    Delete
    --------------------------------------------------
    """

    def delete_books_by_id(self, book_ids: list):
        """
        Deletes the books with the given IDs from the database.
        """
        try:
            self.session.query(Book).filter(Book.id.in_(book_ids)).delete()
            self.session.commit()
            
            # Return the number of books deleted
            return {"success": True, "message": f"{len(book_ids)} Book{'' if len(book_ids) == 1 else 's'} deleted successfully"}
        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": f"An unexpected error occurred"}
