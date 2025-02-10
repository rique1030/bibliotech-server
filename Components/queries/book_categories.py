from sqlalchemy import alias, func
from sqlalchemy.orm import Session
from .query_helper import QueryHelper
from ..tables.models import BookCategory, Category

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
             
            self.session.commit()
            # Return the number of book categories inserted
            return { "success": True, "message": "Book categories inserted successfully" }
        except Exception as e:
            self.session.rollback()
            print(e)
            return { "success": False, "message": str(e) }
    
    """
    Select
    --------------------------------------------------
    """
    def get_book_categories_by_access_number(self, book_access_numbers: list) -> list:
        """
        Returns a list of book categories with the given IDs from the database.
        """
        try:
            result = self.session.query(BookCategory).filter(BookCategory.book_access_number.in_(book_access_numbers)).all()
            return self.query_helper.model_to_dict(result)
        except Exception as e:
            self.session.rollback()
            raise e


    def get_paged_category_count(
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
            categoryAlias = alias(Category)  # This creates an alias for the Category table

            query = self.session.query(
                categoryAlias.c.name,  # Category name
                categoryAlias.c.description,  # Category description
                func.count(BookCategory.book_access_number).label("book_count"),
                # func.group_concat(BookCategory.book_access_number).label("book_access_numbers")
            ).join(BookCategory, categoryAlias.c.id == BookCategory.category_id).group_by(categoryAlias.c.name, categoryAlias.c.description)

            if filters:
                for column, value in filters.items():
                    try:
                        # Safely apply filters dynamically
                        if column in ['name', 'description']:  # Special case for Category table
                            column_attr = getattr(categoryAlias.c, column, None)  # Look up in Category alias
                        else:
                            column_attr = getattr(BookCategory, column, None)  # Look up in BookCategory table
                        if column_attr is None:
                            raise Exception(f"Column '{column}' not found")
                        query = query.filter(column_attr.like(f"%{value}%"))
                    except Exception as e:
                        raise Exception(f"Invalid filter: {e}")
                    
            total_count = query.count()
            offset = page * per_page
            query = query.offset(offset).limit(per_page)
            result = query.all()

            data = []
            for row in result:
                data.append({
                    "name": row.name,
                    "description": row.description,
                    "book_count": row.book_count,
                    # "book_access_numbers": row.book_access_numbers
                })
            return {"success": True, "data": data, "total_count": total_count}
            
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

    def delete_book_categories_by_access_number_and_category_id(self, entries: list):
        """
        Deletes the book categories with the given access number and category ID from the database.
        """
        try:
            grouped_entries = {}
            for entry in entries:
                grouped_entries.setdefault(entry["book_access_number"], []).append(entry["category_id"])

            # Perform batch deletion
            for book_access_number, category_ids in grouped_entries.items():
                self.session.query(BookCategory).filter(
                    BookCategory.book_access_number == book_access_number,
                    BookCategory.category_id.in_(category_ids)
                ).delete(synchronize_session=False)

            self.session.commit()

            return {
                "success": True, "message": "Book categories deleted successfully"}
            # Return the number of book categories deleted
        except Exception as e:
            self.session.rollback()
            print(e)
            return { "success": False, "message": str(e) }