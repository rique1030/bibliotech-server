import logging
# from gevent.sqlalchemy import make_psql_engine
# from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, scoped_session
from Components.config import *

class Database:
    
    def __init__(self):

        self.SQL_CONFIG = None

        if DEPLOYMENT_MODE == DeploymentMode.DEVELOPMENT:
            self.SQL_CONFIG = DEVELOPMENT_CONFIG
        else:
            self.SQL_CONFIG = PRODUCTION_CONFIG

        self.engine = create_async_engine(
            f"mysql+aiomysql://{self.SQL_CONFIG['DB_USER']}:{self.SQL_CONFIG['DB_PASSWORD']}@"
            f"{self.SQL_CONFIG['DB_HOST']}:{self.SQL_CONFIG['DB_PORT']}/{self.SQL_CONFIG['DB_NAME']}",
            pool_size=20,
            max_overflow=10,
            pool_timeout=120,
            pool_recycle=3600,
            pool_pre_ping=False
        )
        
        self.Session = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )

        

    async def init_db(self):
        try:
            from .tables.models import Base
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")

    async def get_session(self):
        async with self.Session() as session:
            yield session

