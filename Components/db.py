import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from Components.config import *


class Database:

    def __init__(self):

        self.SQL_CONFIG = None

        if DEPLOYMENT_MODE == DeploymentMode.DEVELOPMENT:
            self.SQL_CONFIG = DEVELOPMENT_CONFIG
            # logging.basicConfig(level=logging.DEBUG)
        else:
            self.SQL_CONFIG = PRODUCTION_CONFIG
            
        # alchemy
        self.engine = create_engine(
            f"mysql+pymysql://{self.SQL_CONFIG['DB_USER']}:{self.SQL_CONFIG['DB_PASSWORD']}@"
            f"{self.SQL_CONFIG['DB_HOST']}:{self.SQL_CONFIG['DB_PORT']}/{self.SQL_CONFIG['DB_NAME']}",
            # echo=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=60,
            pool_pre_ping=True

        )
        
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        try:
            from .tables.models import Base
            Base.metadata.create_all(self.engine)
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")



