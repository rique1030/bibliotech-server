from datetime import timedelta, datetime
from sqlalchemy import Date, func
from sqlalchemy.orm import Session, aliased
from .query_helper import QueryHelper
from ..tables.models import Book, BorrowedBook, User

class BorrowedBookQueries:
    def __init__(self, session: Session):
        self.session = session  
        self.query_helper = QueryHelper(session)
    """
    Insert
    --------------------------------------------------
    """
    def insert_book_borrow(self, book: dict, user: dict, span: int = 1):
        """
        Inserts borrowed books into the database.
        """
        entry = {
            "book_id": book.get("id"),
            "user_id": user.get("id"),
            "borrowed_date": datetime.now(),
            "due_date": datetime.now() + timedelta(days=span)
            }
        
        update_entry = {
            "id": book.get("id"),
            "status": "borrowed"
        }

        try:
            self.session.bulk_update_mappings(Book, [update_entry,])
            self.session.bulk_insert_mappings(BorrowedBook, [entry,])
            self.session.commit()
            # Return the number of book categories inserted
            return { "success": True, "message": "Book borrowed successfully" }
        except Exception as e:
            self.session.rollback()
            print(e)
            return { "success": False, "message": str(e) }
    
    """
    Delete
    --------------------------------------------------
    """
    def delete_book_borrow_by_id(self, book: dict, user: dict):
        book_id = book.get("id")
        user_id = user.get("id")

        update_entry = {
            "id": book.get("id"),
            "status": "available"
        }
        """
        Deletes the borrowed book with the given ID from the database.
        """
        try:
            self.session.bulk_update_mappings(Book, [update_entry,])
            self.session.query(BorrowedBook).filter(BorrowedBook.book_id == book_id, BorrowedBook.user_id == user_id).delete()
            self.session.commit()
            # Return the number of book categories deleted
            return { "success": True, "message": "Book borrowed deleted successfully" }
        except Exception as e:
            self.session.rollback()
            print(e)
            return { "success": False, "message": str(e) }
        
    def get_borrowed_books(self,    
            page: int = 0,
            per_page:  int = 15,
            filters: dict = None, 
            order_by: str = "id", 
            order_direction: str = "asc"
            ):
        """
        Returns the number of books in the database.
        """
        try:
            BookAlias = aliased(Book)
            UserAlias = aliased(User)

            query = self.session.query(
                BorrowedBook.id,
                UserAlias.first_name,
                UserAlias.last_name,
                BookAlias.access_number,
                BookAlias.title,
                BookAlias.author,
                BorrowedBook.borrowed_date,
                BorrowedBook.due_date,
            ).join(
                BookAlias, BorrowedBook.book_id == BookAlias.id
            ).join(
                UserAlias, BorrowedBook.user_id == UserAlias.id
            )

            # Handle search
            if filters:
                for column, value in filters.items():
                    try:
                        query = query.filter(getattr(Book, column).like(f"%{value}%"))
                    except Exception as e:
                        raise Exception(f"Invalid filter: {e}")
            
            
            total_count = self.session.query(func.count().label("total_count")).select_from(query.subquery()).scalar()
            # total_count = query.count()
            # * pagination
            offset = page * per_page
            query = query.offset(offset).limit(per_page)
            result = query.all()
            
            data = []
            for row in result:
                data.append({
                    "id": row.id,
                    "first_name": row.first_name,
                    "last_name": row.last_name,
                    "access_number": row.access_number,
                    "title": row.title,
                    "author": row.author,
                    "borrowed_date": row.borrowed_date,
                    "due_date": row.due_date
                })
            
            return {
                "total_count": total_count,
                "data": data
            }
            
            # return {"total_count": total_count, "data": self.query_helper.model_to_dict(result)}
        except Exception as e:
            self.session.rollback()
            raise e