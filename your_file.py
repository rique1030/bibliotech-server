async def get_borrowed_books(self, user_id: str):
    async def operation(session):
        catalog = aliased(Catalog)
        copy = aliased(Copy)
        result = await session.execute(select(
            BorrowedBook, 
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
            .join(copy, BorrowedBook.copy_id == copy.id)
            .join(catalog, copy.catalog_id == catalog.id)
            .where(BorrowedBook.user_id == user_id))
        
        rows = result.all()
        borrowed_books = []
        
        for row in rows:
            borrowed_book = row[0]  # First element is the BorrowedBook object
            borrowed_book_dict = {
                "id": borrowed_book.id,
                "user_id": borrowed_book.user_id,
                "copy_id": borrowed_book.copy_id,
                "borrowed_date": borrowed_book.borrowed_date,
                "due_date": borrowed_book.due_date,
                "access_number": row[1],
                "status": row[2],
                "catalog_id": row[3],
                "call_number": row[4],
                "title": row[5],
                "author": row[6],
                "publisher": row[7],
                "cover_image": row[8],
                "description": row[9]
            }
            borrowed_books.append(borrowed_book_dict)
        
        return {"data": borrowed_books, "message": "User fetched successfully"}
