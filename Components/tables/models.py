import re
from enum import Enum
from sqlalchemy.orm import declarative_base , relationship, validates, backref
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum  
from sqlalchemy.sql import func 

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(255), nullable=False, unique=True)
    account_view = Column(Boolean, nullable=False)
    account_insert = Column(Boolean, nullable=False)
    account_update = Column(Boolean, nullable=False)
    account_delete = Column(Boolean, nullable=False)
    roles_view = Column(Boolean, nullable=False)
    roles_insert = Column(Boolean, nullable=False)
    roles_update = Column(Boolean, nullable=False)
    roles_delete = Column(Boolean, nullable=False)
    books_view = Column(Boolean, nullable=False)
    books_insert = Column(Boolean, nullable=False)
    books_update = Column(Boolean, nullable=False)
    books_delete = Column(Boolean, nullable=False)
    categories_view = Column(Boolean, nullable=False)
    categories_insert = Column(Boolean, nullable=False)
    categories_update = Column(Boolean, nullable=False)
    categories_delete = Column(Boolean, nullable=False)
    notes = Column(String(255), nullable=True)
    color = Column(String(7), nullable=False)
    
    users = relationship("User", back_populates="role", cascade="all, delete-orphan")

    @validates('color')
    def validate_color(self, key, value):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise ValueError("Invalid hex color code")
        return value
    


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_pic = Column(String(255), nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    school_id = Column(String(10), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), server_default="2",  nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    role = relationship("Role", back_populates="users")
    borrowed_books = relationship("BorrowedBook", back_populates="user")

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    access_number = Column(String(255), nullable=False, unique=True)
    call_number = Column(String(255), nullable=False )
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False, default="Unknown")
    publisher = Column(String(255), nullable=False, default="Unknown")
    cover_image = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    qrcode = Column(String(255), nullable=False, unique=True)
    date_added = Column(DateTime, nullable=False, default=func.now())
    date_updated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    status = Column(Enum('available', 'borrowed', 'lost', name='book_status'), nullable=False, default='available')

    borrowed_books = relationship("BorrowedBook", back_populates="book")
    categories = relationship("BookCategory", back_populates="book")
    popularity = relationship("BookPopularity", back_populates="book")

class BookCategory(Base):
    __tablename__ = 'book_categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_access_number = Column(
        String(255), 
        ForeignKey('books.access_number', ondelete="CASCADE"), 
        nullable=False
    )
    category_id = Column(
        Integer, 
        ForeignKey('categories.id', ondelete="CASCADE"), 
        nullable=False
    )

    book = relationship("Book", back_populates="categories")
    category = relationship("Category", back_populates="books")


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    
    books = relationship(
        "BookCategory", 
        back_populates="category", 
        cascade="all, delete-orphan", 
        passive_deletes=True
    )

class BorrowedBook(Base):
    __tablename__ = 'borrowed_books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    borrowed_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)

    book = relationship("Book", back_populates="borrowed_books")
    user = relationship("User", back_populates="borrowed_books")

class BookPopularity(Base):
    __tablename__ = 'book_popularity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    borrow_count = Column(Integer, default=0, nullable=False)
    last_borrowed = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="popularity")



# class AuditLog(Base):
#     __tablename__ = 'audit_logs'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     action = Column(String(255), nullable=False)
#     table_name = Column(String(255), nullable=False)
#     record_id = Column(Integer, nullable=False)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     timestamp = Column(DateTime, default=func.now(), nullable=False)

#     user = relationship("User", back_populates="audit_logs")

# class BookInventory(Base):
#     __tablename__ = 'book_inventory'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
#     available_count = Column(Integer, nullable=False)
#     total_count = Column(Integer, nullable=False)

#     book = relationship("Book", back_populates="inventory")

# class UserActivity(Base):
#     __tablename__ = 'user_activities'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     borrow_count = Column(Integer, default=0)
#     overdue_count = Column(Integer, default=0)
#     last_borrowed = Column(DateTime, nullable=True)

#     user = relationship("User", back_populates="activities")

# class BookHistory(Base):
#     __tablename__ = 'book_history'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
#     borrow_count = Column(Integer, default=0)
#     last_borrowed_date = Column(DateTime, nullable=True)

#     book = relationship("Book", back_populates="history")
