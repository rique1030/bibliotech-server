import re
from enum import Enum
import uuid
from sqlalchemy.orm import declarative_base , relationship, validates, backref
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum  
from sqlalchemy.sql import func 

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_pic = Column(String(255), nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    school_id = Column(String(10), nullable=False)
    role_id = Column(String(36), ForeignKey('roles.id'), server_default="2",  nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    role = relationship("Role", back_populates="users")
    borrowed_books = relationship("BorrowedBook", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
        }

class Catalog(Base):
    __tablename__ = 'catalog'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    call_number = Column(String(255), nullable=False )
    title = Column(String(255), nullable=False, unique=True)
    author = Column(String(255), nullable=False, default="Unknown")
    publisher = Column(String(255), nullable=False, default="Unknown")
    cover_image = Column(String(255), nullable=True, default="default")
    description = Column(String(255), nullable=True)
    copies = relationship("Copy", back_populates="catalog", cascade="all, delete-orphan")
    categories = relationship("BookCategory", back_populates="catalog", cascade="all, delete-orphan")

class Copy(Base):
    __tablename__ = 'copy'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    catalog_id = Column(String(36), ForeignKey('catalog.id'), nullable=False)
    access_number = Column(String(255), nullable=False, unique=True)
    status = Column(Enum('available', 'borrowed', 'lost', name='book_status'), nullable=False, default='available')

    catalog = relationship("Catalog", back_populates="copies")
    borrowed_books = relationship("BorrowedBook", back_populates="copies", cascade="all, delete-orphan")

class BookCategory(Base):
    __tablename__ = 'book_categories'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id = Column(String(36), ForeignKey('catalog.id'), nullable=False)
    category_id = Column(String(36), ForeignKey('categories.id', ondelete="CASCADE"), nullable=False)

    catalog = relationship("Catalog", back_populates="categories")
    category = relationship("Category", back_populates="books")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    copy_id = Column(String(36), ForeignKey('copy.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    borrowed_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    copies = relationship("Copy", back_populates="borrowed_books")
    user = relationship("User", back_populates="borrowed_books")
