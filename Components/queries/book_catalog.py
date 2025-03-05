from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .query_helper import QueryHelper
from ..tables.models import Book
from ..QRManager import QRManager
from sqlalchemy import func

class BookCatalogQueries:
    def __init__(self, session_factory: Session):
        self.qr = QRManager()        
        self.session_factory = session_factory
        self.query_helper = QueryHelper(session_factory)


    